from __future__ import annotations

import re


class TextParser:
    ABBREVIATIONS: set[str] = {
        "Dr",
        "Mr",
        "Mrs",
        "Ms",
        "Prof",
        "Sr",
        "Jr",
        "St",
        "vs",
        "etc",
        "e.g",
        "i.e",
    }
    PAUSE_PATTERN: re.Pattern[str] = re.compile(r"\[pause:(\d+(?:\.\d+)?)s\]")
    SENTENCE_PATTERN: re.Pattern[str] = re.compile(r"(?<=[.!?。！？；])\s*")

    @staticmethod
    def split_paragraphs(text: str) -> list[str]:
        parts = re.split(r"\n{2,}", text)
        return [p.strip() for p in parts if p.strip()]

    @staticmethod
    def _is_chinese_sentence_end(char: str) -> bool:
        return char in "。！？；"

    @staticmethod
    def split_sentences(text: str) -> list[str]:
        if not text.strip():
            return []

        result: list[str] = []
        current = 0
        i = 0
        while i < len(text):
            if text[i] in ".!?。！？；":
                char = text[i]
                if TextParser._is_chinese_sentence_end(char):
                    end = i + 1
                    sentence = text[current:end].strip()
                    if sentence:
                        result.append(sentence)
                        current = end
                    i += 1
                    continue

                preceding_word = ""
                j = i - 1
                while j >= 0 and text[j].isalpha():
                    preceding_word = text[j] + preceding_word
                    j -= 1

                if char == "." and preceding_word in TextParser.ABBREVIATIONS:
                    i += 1
                    continue

                end = i + 1
                while end < len(text) and text[end] == " ":
                    if end + 1 < len(text) and text[end + 1] not in " \n":
                        break
                    end += 1

                sentence = text[current:end].strip()
                if sentence:
                    remaining = text[end:].lstrip()
                    if remaining:
                        result.append(sentence)
                        current = end
                        while current < len(text) and text[current] == " ":
                            current += 1
                    else:
                        result.append(sentence)
                        current = len(text)
                i += 1
            else:
                i += 1

        if current < len(text):
            remainder = text[current:].strip()
            if remainder:
                result.append(remainder)

        return result

    @staticmethod
    def parse_pause_markers(text: str) -> list[dict[str, str | float]]:
        parts: list[dict[str, str | float]] = []
        last_end = 0
        for match in TextParser.PAUSE_PATTERN.finditer(text):
            if match.start() > last_end:
                parts.append(
                    {"type": "text", "content": text[last_end : match.start()]}
                )
            parts.append({"type": "pause", "duration": float(match.group(1))})
            last_end = match.end()
        if last_end < len(text):
            parts.append({"type": "text", "content": text[last_end:]})
        if not parts:
            parts.append({"type": "text", "content": text})
        return parts

    @staticmethod
    def insert_auto_pauses(text: str, sentence_pause: float = 0.0, paragraph_pause: float = 0.0) -> str:
        if paragraph_pause > 0:
            text = re.sub(
                r"\n{2,}",
                f" [pause:{paragraph_pause}s]. ",
                text,
            )

        if sentence_pause > 0:

            def replace_sentence_break(m: re.Match[str]) -> str:
                after = m.end()
                preceding = text[: m.start()]
                char = m.group(0).strip()
                if char == ".":
                    word_before = ""
                    j = m.start() - 1
                    while j >= 0 and preceding[j].isalpha():
                        word_before = preceding[j] + word_before
                        j -= 1
                    if word_before in TextParser.ABBREVIATIONS:
                        return m.group(0)
                if after < len(text) and "[pause:" in text[after:]:
                    remaining = text[after:]
                    if remaining.lstrip().startswith("[pause:"):
                        return m.group(0)
                return f" [pause:{sentence_pause}s] "

            text = TextParser.SENTENCE_PATTERN.sub(replace_sentence_break, text)

        return text

    @staticmethod
    def get_segments(text: str, sentence_pause: float = 0.0, paragraph_pause: float = 0.0) -> list[dict[str, str | float]]:
        processed = TextParser.insert_auto_pauses(text, sentence_pause, paragraph_pause)
        return TextParser.parse_pause_markers(processed)
