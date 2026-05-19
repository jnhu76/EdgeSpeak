from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Locale:
    code: str
    name: str


SUPPORTED_LOCALES = [
    Locale("en", "English"),
    Locale("zh", "中文"),
]

_STRINGS_DB: dict[str, dict[str, str]] = {
    "zh": {
        "app.title": "🔊 TTS 语音工具",
        "voice.label": "🎙️ 语音",
        "voice.accent": "口音",
        "voice.select": "选择语音",
        "voice.language": "🌐 语言",
        "voice.all_languages": "全部",
        "text.placeholder": "在此粘贴或输入文本，或导入文件...",
        "text.import": "📂 导入",
        "text.insert_pause": "⏸ 停顿",
        "text.clear": "🗑 清空",
        "pause.sentence": "句间停顿",
        "pause.paragraph": "段间停顿",
        "pause.auto": "自动停顿",
        "pause.unit": "秒",
        "settings.title": "⚙️ 设置",
        "settings.speed": "⚡ 语速",
        "settings.pitch": "🎵 音调",
        "settings.volume": "🔊 音量",
        "settings.normal": "正常",
        "settings.slow": "慢",
        "settings.slower": "更慢",
        "settings.fast": "快",
        "settings.faster": "更快",
        "action.generate": "▶ 生成音频",
        "action.generating": "⏳ 正在生成...",
        "action.cancel": "⏹ 停止生成",
        "action.save_mp3": "💾 保存 MP3",
        "action.save_srt": "📝 保存字幕",
        "action.preview": "👂 试听",
        "player.play": "▶ 播放",
        "player.pause": "⏸ 暂停",
        "player.stop": "⏹ 停止",
        "status.ready": "✅ 就绪",
        "status.generating": "⏳ 正在生成第 {current}/{total} 段...",
        "status.complete": "✅ 音频已生成！时长 {duration}",
        "status.error": "❌ 错误：{error}",
        "status.cancelled": "⏹ 已取消生成",
        "file.text_files": "文本文件",
        "file.audio_files": "音频文件",
        "file.subtitle_files": "字幕文件",
        "file.all_files": "所有文件",
        "dialog.import_title": "导入文本文件",
        "dialog.save_audio_title": "保存音频",
        "dialog.save_srt_title": "保存字幕",
        "language.en": "English",
        "language.zh": "中文",
        "warning.no_text": "请输入文本以生成音频。",
        "warning.no_voice": "请选择一个语音。",
        "warning.no_text_title": "无文本",
        "warning.no_voice_title": "无语音",
        "error.generation": "生成错误",
        "info.preview": "请在编辑器中选择文本以试听。",
    },
    "en": {
        "app.title": "🔊 TTS Tool",
        "voice.label": "🎙️ Voice",
        "voice.accent": "Accent",
        "voice.select": "Select Voice",
        "voice.language": "🌐 Language",
        "voice.all_languages": "All",
        "text.placeholder": "Paste or type your text here, or import a file...",
        "text.import": "📂 Import",
        "text.insert_pause": "⏸ Pause",
        "text.clear": "🗑 Clear",
        "pause.sentence": "Sentence pause",
        "pause.paragraph": "Paragraph pause",
        "pause.auto": "Auto-pause",
        "pause.unit": "s",
        "settings.title": "⚙️ Settings",
        "settings.speed": "⚡ Speed",
        "settings.pitch": "🎵 Pitch",
        "settings.volume": "🔊 Volume",
        "settings.normal": "Normal",
        "settings.slow": "Slow",
        "settings.slower": "Slower",
        "settings.fast": "Fast",
        "settings.faster": "Faster",
        "action.generate": "▶ Generate",
        "action.generating": "⏳ Generating...",
        "action.cancel": "⏹ Cancel",
        "action.save_mp3": "💾 Save MP3",
        "action.save_srt": "📝 Save SRT",
        "action.preview": "👂 Preview",
        "player.play": "▶ Play",
        "player.pause": "⏸ Pause",
        "player.stop": "⏹ Stop",
        "status.ready": "✅ Ready",
        "status.generating": "⏳ Generating segment {current}/{total}...",
        "status.complete": "✅ Audio generated! {duration}",
        "status.error": "❌ Error: {error}",
        "status.cancelled": "⏹ Generation cancelled",
        "file.text_files": "Text Files",
        "file.audio_files": "Audio Files",
        "file.subtitle_files": "Subtitle Files",
        "file.all_files": "All Files",
        "dialog.import_title": "Import Text File",
        "dialog.save_audio_title": "Save Audio As",
        "dialog.save_srt_title": "Save Subtitles As",
        "language.en": "English",
        "language.zh": "中文",
        "warning.no_text": "Please enter some text to generate audio.",
        "warning.no_voice": "Please select a voice.",
        "warning.no_text_title": "No Text",
        "warning.no_voice_title": "No Voice",
        "error.generation": "Generation Error",
        "info.preview": "Select some text in the editor to preview.",
    },
}

_current_locale = "zh"
_strings: dict[str, str] = _STRINGS_DB["zh"]


def set_locale(code: str) -> None:
    global _current_locale, _strings
    _current_locale = code
    _strings = _STRINGS_DB.get(code, {})


def get_locale() -> str:
    return _current_locale


def t(key: str, **kwargs) -> str:
    template = _strings.get(key, key)
    if kwargs:
        return template.format(**kwargs)
    return template
