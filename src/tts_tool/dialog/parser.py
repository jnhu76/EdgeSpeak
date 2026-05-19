from __future__ import annotations

import re

from tts_tool.dialog.models import DialogCharacter, DialogScript, DialogTurn

_SPEAKER_RE = re.compile(r"^\[([^\]]+)\]\s*(.*)")
_CHAR_BLOCK_START = "---characters---"
_CHAR_BLOCK_END = "---end---"


class DialogParser:
    @staticmethod
    def parse(
        text: str,
        inter_turn_pause: float = 0.8,
        paragraph_pause: float = 2.0,
    ) -> DialogScript:
        characters: list[DialogCharacter] = []
        dialog_text = text

        char_block, dialog_text = _extract_character_block(text)
        if char_block:
            characters = _parse_character_block(char_block)

        turns = _parse_turns(dialog_text, paragraph_pause)

        return DialogScript(
            characters=characters,
            turns=turns,
            inter_turn_pause=inter_turn_pause,
            paragraph_pause=paragraph_pause,
        )


def _extract_character_block(text: str) -> tuple[str, str]:
    if _CHAR_BLOCK_START not in text:
        return "", text
    start_idx = text.index(_CHAR_BLOCK_START) + len(_CHAR_BLOCK_START)
    end_idx = text.find(_CHAR_BLOCK_END, start_idx)
    if end_idx == -1:
        return "", text
    block = text[start_idx:end_idx].strip()
    remainder = text[end_idx + len(_CHAR_BLOCK_END):].strip()
    return block, remainder


def _parse_character_block(block: str) -> list[DialogCharacter]:
    characters: list[DialogCharacter] = []
    for line in block.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        name_part, rest = line.split(":", 1)
        name = name_part.strip()
        voice, params = _parse_character_rest(rest.strip())
        characters.append(
            DialogCharacter(
                name=name,
                voice=voice,
                rate=params.get("rate", "+0%"),
                pitch=params.get("pitch", "+0Hz"),
                volume=params.get("volume", "+0%"),
            )
        )
    return characters


def _parse_character_rest(rest: str) -> tuple[str, dict[str, str]]:
    parts = [p.strip() for p in rest.split(",")]
    voice = parts[0] if parts else ""
    params: dict[str, str] = {}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            params[k.strip()] = v.strip()
    return voice, params


def _parse_turns(text: str, paragraph_pause: float) -> list[DialogTurn]:
    turns: list[DialogTurn] = []
    current_speaker = ""
    lines = text.split("\n")
    pending_pause = 0.0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            pending_pause += paragraph_pause
            continue

        match = _SPEAKER_RE.match(stripped)
        if match:
            current_speaker = match.group(1).strip()
            content = match.group(2).strip()
            if content:
                turns.append(
                    DialogTurn(
                        speaker=current_speaker,
                        text=content,
                        paragraph_pause=pending_pause,
                    )
                )
                pending_pause = 0.0
        else:
            content = stripped
            turns.append(
                DialogTurn(
                    speaker=current_speaker,
                    text=content,
                    paragraph_pause=pending_pause,
                )
            )
            pending_pause = 0.0

    return turns
