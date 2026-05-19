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
