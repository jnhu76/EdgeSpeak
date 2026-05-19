# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

SRC = Path(SPECPATH) / "src"

_hiddenimports = [
    "tts_tool",
    "tts_tool.text_parser",
    "tts_tool.config",
    "tts_tool.subtitle",
    "tts_tool.tts_engine",
    "tts_tool.tts_provider",
    "tts_tool.voice_list",
    "tts_tool.audio_player",
    "tts_tool.i18n",
    "tts_tool.providers",
    "tts_tool.providers.edge_provider",
    "tts_tool.gui",
    "tts_tool.gui.api",
    "tts_tool.gui.app",
    "edge_tts",
    "edge_tts.communicate",
    "edge_tts.voices",
    "edge_tts.submaker",
    "edge_tts.typing",
    "pygame",
    "webview",
    "webview.platforms",
]
if sys.platform == "win32":
    _hiddenimports += [
        "webview.platforms.winforms",
        "clr_loader",
        "pythonnet",
    ]
else:
    _hiddenimports += [
        "webview.platforms.gtk",
        "webview.platforms.cocoa",
    ]

_datas = [
    (str(SRC / "tts_tool" / "gui" / "index.html"), "tts_tool/gui"),
]

_icon = None
if sys.platform == "win32":
    _icon = str(SRC / "tts_tool" / "gui" / "icon.ico")
    _datas.append((str(SRC / "tts_tool" / "gui" / "icon.ico"), "tts_tool/gui"))

a = Analysis(
    [str(SRC / "tts_tool" / "__main__.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=_datas,
    hiddenimports=_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "PySide6",
        "shiboken6",
        "unittest",
        "test",
        "tests",
        "pytest",
        "hypothesis",
        "ruff",
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="tts-tool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)
