# EdgeSpeak - Project Constitution

## Project Identity

- **Name:** EdgeSpeak
- **Purpose:** Cross-platform TTS desktop tool with generation history
- **Runtime:** Python 3.12+
- **Package Manager:** uv
- **Virtual Environment:** `.venv/` (managed by uv)
- **Key Dependencies:** edge-tts, pywebview, pygame

## Architecture

```
edgespeak/
├── src/tts_tool/
│   ├── __main__.py          Entry point
│   ├── tts_provider.py      TTSProvider ABC (strategy pattern)
│   ├── providers/
│   │   └── edge_provider.py Edge TTS implementation
│   ├── tts_engine.py        TTSEngine facade
│   ├── text_parser.py       Text splitting, pause insertion
│   ├── config.py            SpeedPreset, AppConfig
│   ├── subtitle.py          SRT generation
│   ├── voice_list.py        Voice fetching and filtering
│   ├── audio_player.py      pygame-based playback
│   ├── i18n.py              Internationalization
│   ├── job.py               Job + JobStore (generation history model)
│   └── gui/
│       ├── app.py           pywebview entry point
│       ├── api.py           Python-JS bridge (Api class)
│       ├── index.html       HTML/CSS/JS frontend (toolbox theme)
│       └── icon.ico         Application icon
├── tests/
├── pyproject.toml
└── tts-tool.spec            PyInstaller build spec
```

## Code Style

- **Formatter:** ruff (format + lint)
- **Line length:** 88 chars
- **Type hints:** required on all public functions
- **No comments** unless user explicitly asks
- **No emoji** in UI labels — text only
- `pathlib.Path` for all file paths
- `asyncio` for all edge-tts calls
- Thread-safe: TTS runs in background thread, pywebview on main thread

## Before Every Commit

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run pytest tests/ -v
```

## GUI Rules

- **Framework:** pywebview (native WebView2 on Windows)
- **Frontend:** Single `index.html` with inline CSS and JS, no external dependencies
- **Theme:** Toolbox/hardware style — 2px borders, inset shadows, square-ish corners
- **Font sizes:** 13-14px minimum, no tiny text
- **Buttons:** Raised 3D appearance with hover/active states
- **JS-Python bridge:** `window.pywebview.api` after `pywebviewready` event
- All API calls from JS are async

## Testing

- Framework: pytest
- 181 tests covering: text parsing, subtitle generation, TTS engine, job/store, cancellation, voice filtering, i18n, config
- Mock edge-tts network calls (no real API calls in CI)

## Dependency Policy

- **Runtime:** edge-tts, pygame, pywebview
- **Dev:** ruff, pytest, pytest-asyncio, hypothesis, pyinstaller, pillow
- Keep dependencies minimal

## Build

- **Windows:** `uv run pyinstaller tts-tool.spec --clean --noconfirm` → `dist/tts-tool.exe` (~19 MB)
- **Linux:** Requires GTK + WebKit2
- **macOS:** Uses system WebKit
