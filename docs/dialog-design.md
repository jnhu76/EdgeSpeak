# EdgeSpeak Dialog Mode - Design Document

## 1. Overview

Dialog mode extends EdgeSpeak to generate conversational audio with multiple speakers.
Users define characters (name + voice), write dialog text with speaker labels,
and the system generates per-turn audio segments then merges them into a single MP3.

## 2. Text Format

### 2.1 Inline Speaker Tags

```
[男] 你好，请问你是哪里人？
[女] 我是北京人，你呢？
[男] 我是上海人。你来北京多久了？
[旁白] 两人相视而笑。
[女] 三年了，已经习惯了。
```

Rules:
- Tag format: `[角色名]` at the start of a line or inline before text
- `[旁白]` is a special tag: uses a configurable narrator voice, slightly slower rate
- If no tag on a line, inherit previous speaker
- Empty lines = paragraph pause (configurable duration)
- Support manual pause markers: `[pause:1.5s]`

### 2.2 Character Definition Block (optional header)

```
---characters---
男: zh-CN-YunxiNeural, rate=+0%, pitch=+0Hz, volume=+0%
女: zh-CN-XiaoxiaoNeural, rate=+0%, pitch=+5Hz, volume=+0%
旁白: zh-CN-YunyangNeural, rate=-10%, pitch=-5Hz, volume=+0%
---end---
```

Rules:
- Optional. If absent, characters must be defined in UI before generating
- Format: `角色名: voice_short_name, key=value, ...`
- Supported keys: `rate`, `pitch`, `volume`

## 3. Character Model

```python
@dataclass
class DialogCharacter:
    name: str
    voice: str              # voice short name
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"
    color: str = "#4f46e5"  # UI highlight color

@dataclass
class DialogTurn:
    speaker: str            # character name
    text: str
    paragraph_pause: float = 0.0  # pause BEFORE this turn

@dataclass
class DialogScript:
    characters: list[DialogCharacter]
    turns: list[DialogTurn]
    inter_turn_pause: float = 0.8   # seconds between turns
    paragraph_pause: float = 2.0    # seconds for empty lines
```

### 3.1 Default Character Presets

| Label   | Suggested Voice (zh-CN)     | Gender | Use Case       |
|---------|-----------------------------|--------|----------------|
| 男      | zh-CN-YunxiNeural           | Male   | Young male     |
| 女      | zh-CN-XiaoxiaoNeural        | Female | Young female   |
| 旁白    | zh-CN-YunyangNeural         | Male   | Narrator, news |
| 老人    | zh-CN-YunjianNeural         | Male   | Older male     |
| 儿童    | zh-CN-XiaoyiNeural          | Female | Child-like     |

For English:
| Label   | Suggested Voice (en-US)     | Gender |
|---------|-----------------------------|--------|
| Male    | en-US-GuyNeural             | Male   |
| Female  | en-US-JennyNeural           | Female |
| Narrator| en-US-AriaNeural            | Female |

## 4. Audio Generation Pipeline

```
Input Text
    ↓
Parse Dialog Script (speaker tags → DialogTurn list)
    ↓
For each turn:
    ├─ Resolve character → voice/rate/pitch/volume
    ├─ Generate single-turn MP3 via TTSProvider
    ├─ Compute turn duration
    └─ Store turn audio bytes
    ↓
Concatenate: turn1.mp3 + silence + turn2.mp3 + silence + ... → combined.mp3
    ↓
Merge SRT boundaries (offset each turn's timestamps)
    ↓
Output: combined audio + combined SRT
```

### 4.1 Concatenation

- Use existing silence frame concatenation from `tts_engine.py`
- Inter-turn silence: configurable (default 0.8s)
- Paragraph pause (empty lines): configurable (default 2.0s)
- No re-encoding: raw MP3 byte concatenation + silence frames

### 4.2 SRT Merging

Each turn generates its own word boundaries. During merge:
- Offset all timestamps by cumulative duration of previous turns + pauses
- Prefix speaker name in SRT text: `[男] 你好，请问你是哪里人？`

## 5. UI Design

### 5.1 Mode Switch

Top of right column: tab bar

```
┌──────────┐ ┌──────────┐
│  单人模式  │ │  对话模式  │
└──────────┘ └──────────┘
```

- Single mode: current UI unchanged
- Dialog mode: replaces right column content

### 5.2 Dialog Mode Layout

```
┌─ Right Column ──────────────────────────────┐
│                                              │
│  ┌─ Character Panel ────────────────────┐    │
│  │ 角色列表                              │    │
│  │ ┌──────────────────────────────────┐ │    │
│  │ │ 男  zh-CN-YunxiNeural   [+0%]  [编辑]│ │    │
│  │ │ 女  zh-CN-XiaoxiaoNeural [+5Hz] [编辑]│ │    │
│  │ │ 旁白 zh-CN-YunyangNeural  [-10%] [编辑]│ │    │
│  │ └──────────────────────────────────┘ │    │
│  │ [添加角色]                            │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌─ Dialog Editor ──────────────────────┐    │
│  │ [男] 你好，请问你是哪里人？            │    │
│  │ [女] 我是北京人，你呢？                │    │
│  │                                       │    │
│  │ [男] 我是上海人。                     │    │
│  │ [旁白] 两人相视而笑。                  │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌─ Toolbar ────────────────────────────┐    │
│  │ [导入]  [模板]  停顿 0.8秒  [生成对话] │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌─ Generation History ─────────────────┐    │
│  │ #1 14:32 3人 5轮 00:15  [播放][MP3][SRT]│    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌─ Player ─────────────────────────────┐    │
│  │ [播放] [停止]           00:00/00:15   │    │
│  │ ═══════════════════════              │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

### 5.3 Character Edit Dialog

When user clicks "编辑" on a character:

```
┌─ 编辑角色 ──────────────────┐
│                              │
│ 角色名: [男        ]         │
│                              │
│ 语言:  [zh-CN       ▼]      │
│ 语音:  [YunxiNeural ▼]      │
│                              │
│ 语速:  ═══●═══  +0%   [R]   │
│ 音调:  ═══●═══  +0Hz  [R]   │
│ 音量:  ═══●═══  +0%   [R]   │
│                              │
│      [确定]    [取消]        │
└──────────────────────────────┘
```

### 5.4 Dialog Templates

Pre-built templates for common scenarios:

1. **男女对话** — Male + Female, 2 characters
2. **采访** — Host + Guest + Narrator, 3 characters
3. **故事** — Narrator + multiple characters
4. **课堂** — Teacher + Student
5. **自定义** — Empty, user defines everything

### 5.5 Visual Differences from Single Mode

| Element          | Single Mode         | Dialog Mode                 |
|------------------|---------------------|-----------------------------|
| Tab bar          | Hidden              | Shown (Single / Dialog)     |
| Left column      | Voice + Settings    | Settings only (shared)      |
| Text editor      | Plain textarea      | Color-coded speaker tags    |
| Generate button  | "生成音频"          | "生成对话"                   |
| History items    | Voice + rate + time | Characters + turns + time   |
| Player           | Same                | Same                        |

## 6. Color Coding for Speakers

Pre-defined palette for speaker highlighting:

```python
SPEAKER_COLORS = [
    "#4f46e5",  # Indigo   — first speaker
    "#dc2626",  # Red      — second speaker
    "#16a34a",  # Green    — third speaker
    "#d97706",  # Amber    — fourth speaker
    "#7c3aed",  # Violet   — fifth speaker
    "#0891b2",  # Cyan     — sixth speaker
]
```

In the editor:
- `[男]` rendered in indigo background
- `[女]` rendered in red background
- `[旁白]` rendered in green background
- Speaker tags are read-only badges, not editable text

## 7. API Changes

### New methods in `api.py`:

```python
def get_dialog_templates() -> list[dict]
def parse_dialog_text(text: str) -> dict        # returns {characters, turns}
def generate_dialog(text: str, characters: list[dict], inter_pause: float, para_pause: float) -> str
def get_dialog_history() -> list[dict]           # dialog-specific history items
```

### `generate_dialog` flow:

1. Parse text into `DialogTurn` list
2. Resolve each turn's character to voice params
3. For each turn: call `TTSEngine.generate_full()` with that character's params
4. Concatenate all turn audio bytes with silence frames
5. Merge SRT boundaries with cumulative offsets
6. Store as history item with `type: "dialog"`, `characters: [...]`, `turn_count: N`
7. Return combined audio_b64 + duration + merged boundaries

## 8. File Structure Changes

```
src/tts_tool/
  dialog/
    __init__.py
    parser.py        # Dialog text parser (tag extraction)
    models.py        # DialogCharacter, DialogTurn, DialogScript
    merger.py        # Audio concatenation + SRT merge
    templates.py     # Pre-built dialog templates
    presets.py       # Default character voice mappings per language
  gui/
    api.py           # + dialog API methods
    index.html       # + dialog mode UI (tab switch, character panel, dialog editor)
```

## 9. Testing Plan

### Unit Tests
- `test_dialog_parser.py`: Parse speaker tags, handle missing tags, empty lines, nested brackets
- `test_dialog_models.py`: DialogCharacter, DialogTurn, DialogScript validation
- `test_dialog_merger.py`: Audio byte concatenation, silence insertion, SRT offset calculation
- `test_dialog_presets.py`: Default voice mapping per language

### Integration Tests
- End-to-end: parse text → generate turns → merge → verify output duration ≈ sum of turns + pauses
- Cancel mid-generation: stop after turn 2 of 5

### Edge Cases
- Single speaker dialog (all turns same character)
- Empty turn text (skip but keep pause)
- Very long dialog (50+ turns)
- Mixed language in different turns
- Character name with special characters
