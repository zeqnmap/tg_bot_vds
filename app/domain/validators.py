import re


_NAME_PART = r"[А-ЯЁа-яёA-Za-z]+(?:[-'][А-ЯЁа-яёA-Za-z]+)*"
_FULL_NAME_PATTERN = re.compile(rf"{_NAME_PART}(?: {_NAME_PART})*")


def normalize_full_name(value: str) -> str:
    return " ".join(value.strip().split())


def is_valid_full_name(value: str) -> bool:
    normalized = normalize_full_name(value)
    return bool(_FULL_NAME_PATTERN.fullmatch(normalized))
