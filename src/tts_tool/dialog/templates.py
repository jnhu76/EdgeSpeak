from __future__ import annotations

DIALOG_TEMPLATES: list[dict] = [
    {
        "id": "dialog_mf",
        "name": "男女对话",
        "name_en": "Male-Female Dialog",
        "characters": [
            {"name": "男", "voice": "zh-CN-YunxiNeural"},
            {"name": "女", "voice": "zh-CN-XiaoxiaoNeural"},
        ],
        "sample_text": "[男] 你好，请问你是哪里人？\n[女] 我是北京人，你呢？\n[男] 我是上海人。\n[女] 欢迎来北京玩！",
    },
    {
        "id": "interview",
        "name": "采访",
        "name_en": "Interview",
        "characters": [
            {"name": "主持人", "voice": "zh-CN-YunyangNeural"},
            {"name": "嘉宾", "voice": "zh-CN-YunxiNeural"},
            {"name": "旁白", "voice": "zh-CN-YunyangNeural"},
        ],
        "sample_text": "[旁白] 今天我们请到了一位特别嘉宾。\n[主持人] 欢迎来到我们的节目！\n[嘉宾] 谢谢邀请，很高兴来到这里。\n[主持人] 能和大家分享一下你的经历吗？\n[嘉宾] 当然可以。",
    },
    {
        "id": "story",
        "name": "故事",
        "name_en": "Story",
        "characters": [
            {"name": "旁白", "voice": "zh-CN-YunyangNeural"},
            {"name": "小明", "voice": "zh-CN-YunxiNeural"},
            {"name": "小红", "voice": "zh-CN-XiaoxiaoNeural"},
        ],
        "sample_text": "[旁白] 从前有一座山，山里住着两个孩子。\n[小明] 小红，我们去探险吧！\n[小红] 好啊，但我们要早点回来。\n[旁白] 于是他们出发了。",
    },
    {
        "id": "classroom",
        "name": "课堂",
        "name_en": "Classroom",
        "characters": [
            {"name": "老师", "voice": "zh-CN-YunyangNeural"},
            {"name": "学生", "voice": "zh-CN-YunxiNeural"},
        ],
        "sample_text": "[老师] 今天我们学习第三课。\n[学生] 老师，我有个问题。\n[老师] 请说。\n[学生] 这个词是什么意思？\n[老师] 好问题，让我来解释一下。",
    },
]

_TEMPLATE_MAP: dict[str, dict] = {t["id"]: t for t in DIALOG_TEMPLATES}


def get_template(template_id: str) -> dict | None:
    return _TEMPLATE_MAP.get(template_id)
