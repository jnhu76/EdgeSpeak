from __future__ import annotations

DEFAULT_CHARACTERS_ZH: list[dict] = [
    {"name": "男", "voice": "zh-CN-YunxiNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%", "color": "#4f46e5"},
    {"name": "女", "voice": "zh-CN-XiaoxiaoNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%", "color": "#dc2626"},
    {"name": "旁白", "voice": "zh-CN-YunyangNeural", "rate": "-10%", "pitch": "-5Hz", "volume": "+0%", "color": "#16a34a"},
    {"name": "老人", "voice": "zh-CN-YunjianNeural", "rate": "-5%", "pitch": "-10Hz", "volume": "+0%", "color": "#d97706"},
    {"name": "儿童", "voice": "zh-CN-XiaoyiNeural", "rate": "+5%", "pitch": "+5Hz", "volume": "+0%", "color": "#7c3aed"},
]

DEFAULT_CHARACTERS_EN: list[dict] = [
    {"name": "Male", "voice": "en-US-GuyNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%", "color": "#4f46e5"},
    {"name": "Female", "voice": "en-US-JennyNeural", "rate": "+0%", "pitch": "+0Hz", "volume": "+0%", "color": "#dc2626"},
    {"name": "Narrator", "voice": "en-US-AriaNeural", "rate": "-5%", "pitch": "+0Hz", "volume": "+0%", "color": "#16a34a"},
]


_LANG_MAP: dict[str, list[dict]] = {
    "zh": DEFAULT_CHARACTERS_ZH,
    "en": DEFAULT_CHARACTERS_EN,
}


def get_default_characters(language: str) -> list[dict]:
    return list(_LANG_MAP.get(language, []))
