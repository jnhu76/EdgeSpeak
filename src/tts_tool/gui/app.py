from __future__ import annotations

import sys
from pathlib import Path

import webview

from tts_tool.gui.api import Api

ICON_PATH = Path(__file__).parent / "icon.ico"


def main() -> None:
    api = Api()
    html_path = Path(__file__).parent / "index.html"
    window = webview.create_window(
        "TTS 语音工具",
        str(html_path),
        js_api=api,
        width=960,
        height=700,
        min_size=(800, 600),
        resizable=True,
        text_select=True,
    )
    api.set_window(window)

    if sys.platform == "win32" and ICON_PATH.exists():
        webview.start(debug=False, icon=str(ICON_PATH))
    else:
        webview.start(debug=False)


if __name__ == "__main__":
    main()
