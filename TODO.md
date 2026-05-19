# TODO - Dialog Mix Feature

## Phase 1: Core Model & Parser
- [ ] `src/tts_tool/dialog/models.py` — DialogCharacter, DialogTurn, DialogScript dataclasses
- [ ] `src/tts_tool/dialog/parser.py` — Parse `[角色名]` tags, empty lines, pause markers
- [ ] `src/tts_tool/dialog/presets.py` — Default voice mappings (zh/en) per character type
- [ ] `src/tts_tool/dialog/templates.py` — Pre-built templates (男女对话, 采访, 故事, 课堂)
- [ ] Tests: parser, models, presets

## Phase 2: Audio Generation & Merge
- [ ] `src/tts_tool/dialog/merger.py` — MP3 byte concatenation + silence frames
- [ ] SRT boundary merge with cumulative time offsets
- [ ] `api.py`: `generate_dialog()` method — loop turns, generate, merge
- [ ] `api.py`: `parse_dialog_text()` method
- [ ] `api.py`: `get_dialog_templates()` method
- [ ] Tests: merger, SRT offset, integration

## Phase 3: UI — Mode Switch
- [ ] Tab bar: "单人模式" / "对话模式" at top of right column
- [ ] State management: `currentMode = 'single' | 'dialog'`
- [ ] Show/hide panels based on mode

## Phase 4: UI — Character Panel
- [ ] Character list with name + voice + params
- [ ] Add/edit character dialog (voice selector, rate/pitch/volume sliders)
- [ ] Color-coded character badges
- [ ] Delete character

## Phase 5: UI — Dialog Editor
- [ ] Textarea with `[角色名]` tag support
- [ ] Speaker tags rendered as colored badges (read-only)
- [ ] Import dialog text files
- [ ] Template selector dropdown
- [ ] Toolbar: inter-turn pause duration, paragraph pause

## Phase 6: UI — Dialog History & Player
- [ ] History items show: character count + turn count + duration
- [ ] Same player controls (shared with single mode)
- [ ] SRT export with speaker labels

## Design Doc
- [docs/dialog-design.md](docs/dialog-design.md)
