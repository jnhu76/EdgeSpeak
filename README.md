# EdgeSpeak

[中文文档](README_ZH.md)

Cross-platform desktop text-to-speech tool powered by Microsoft Edge TTS.

Built with Python + pywebview (native WebView2) and a clean toolbox-style UI.

## Features

### Voice & Language

- **7 languages**: English, Chinese, Japanese, Korean, French, Russian, Spanish
- **Accent filtering**: Narrow voices by regional accent (e.g. en-US, en-GB, zh-CN, zh-TW)
- **Voice list**: Scrollable voice list with gender and category badges, click to select
- **Locale switcher**: Change UI language at runtime (English / Chinese)

### Audio Generation

- **Configurable parameters**: Rate (-50% to +100%), Pitch (-50Hz to +50Hz), Volume (-50% to +50%)
- **Speed presets**: One-click 0.5x / 1x / 1.5x / 2x
- **Reset buttons**: Quick-reset pitch and volume sliders to default
- **Auto-pause**: Automatically insert silence between sentences and paragraphs (configurable duration)
- **Manual pause**: Insert `[pause:1.5s]` markers at cursor position
- **Text import**: Load text from .txt files
- **Text selection preview**: Select text and click "Preview" to generate only the selection

### Generation History

- Every generation is recorded with timestamp, voice, rate, pitch, volume, duration
- **Per-item actions**: Play, Save MP3, Save SRT, Delete
- Currently playing item is highlighted
- "Clear History" button to start fresh (also clears text and stops playback)
- History persists in memory for the session

### Playback

- **Play / Pause / Stop** controls
- **Progress bar** with seek (drag to any position)
- **Time display**: Current position / total duration
- Audio plays via HTML5 Audio with blob URLs (no external player needed)

### Subtitle Export

- SRT subtitle files with word-level timestamps
- Boundaries synced to generated audio

### Dialog Mode (Multi-Speaker)

- **Mode switch**: Tab bar to switch between Single mode and Dialog mode
- **Character management**: Add/edit/delete characters with voice, rate, pitch, volume settings
- **Color-coded badges**: Each character gets a unique color
- **Templates**: Pre-built templates (Male-Female Dialog, Interview, Story, Classroom)
- **Inter-turn pause**: Configurable silence between turns (default 0.8s)
- **Paragraph pause**: Longer pause at empty lines (default 2.0s)
- **SRT with speaker labels**: Subtitles prefixed with `[Speaker Name]`

#### Dialog Text Format

Use `[SpeakerName]` tags at the start of a line to mark the speaker:

```
[男] 你好，请问你是哪里人？
[女] 我是北京人，你呢？
[男] 我是上海人。

[女] 欢迎来北京玩！
[旁白] 两人相视而笑。
```

**Rules:**
- `[角色名]` must be at the start of the line, followed by the text
- Empty lines = paragraph pause (configurable)
- Lines without a tag inherit the previous speaker
- Optional character definition block at the top:

```
---characters---
男: zh-CN-YunxiNeural, rate=+0%, pitch=+0Hz
女: zh-CN-XiaoxiaoNeural, rate=+0%, pitch=+5Hz
旁白: zh-CN-YunyangNeural, rate=-10%, pitch=-5Hz
---end---
[男] 你好
[女] 你好呀
```

**More examples:**

Interview:
```
[主持人] 欢迎来到我们的节目！
[嘉宾] 谢谢邀请。
[主持人] 能分享一下你的经历吗？
[嘉宾] 当然可以。
```

Story:
```
[旁白] 从前有一座山。
[小明] 小红，我们去探险吧！
[小红] 好啊，但我们要早点回来。
[旁白] 于是他们出发了。
```

### Build & Packaging

- Single-file Windows exe (~19 MB) via PyInstaller
- No console window, custom application icon
- Zero network dependencies for UI (all CSS/JS inline, no CDN)

## Quick Start

### Run from source

```bash
uv sync
uv run python -m tts_tool
```

### Run tests

```bash
uv run pytest tests/ -v
```

### Lint

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

## Build

### Windows

```powershell
uv run pyinstaller tts-tool.spec --clean --noconfirm
```

Output: `dist/tts-tool.exe` (~19 MB, single-file, no console)

### Linux

```bash
sudo apt install libgtk-3-0 libglib2.0-0 libwebkit2gtk-4.1-dev
uv sync
uv run pyinstaller tts-tool.spec --clean --noconfirm
```

### macOS

```bash
uv sync
uv run pyinstaller tts-tool.spec --clean --noconfirm
```

## Architecture

```
src/tts_tool/
  __main__.py          Entry point
  tts_provider.py      TTSProvider ABC (strategy pattern)
  providers/
    edge_provider.py   Edge TTS implementation
  tts_engine.py        TTSEngine facade
  text_parser.py       Sentence/paragraph splitting
  config.py            SpeedPreset, AppConfig
  subtitle.py          SRT generation
  voice_list.py        Voice fetching and filtering
  audio_player.py      pygame-based audio player
  i18n.py              Internationalization
  job.py               Job + JobStore for generation history
  dialog/
    models.py          DialogCharacter, DialogTurn, DialogScript
    parser.py          Dialog text parser ([speaker] tags)
    merger.py          Audio concatenation + SRT boundary merge
    presets.py         Default character voice mappings
    templates.py       Pre-built dialog templates
  gui/
    app.py             pywebview entry point
    api.py             Python-JS bridge (Api class)
    index.html         HTML/CSS/JS frontend (toolbox theme)
    icon.ico           Application icon
```

## Dependencies

- [pywebview](https://pypi.org/project/pywebview/) - Native WebView GUI
- [edge-tts](https://pypi.org/project/edge-tts/) - Microsoft Edge TTS API
- [pygame](https://pypi.org/project/pygame/) - Audio duration computation

## License

MIT
