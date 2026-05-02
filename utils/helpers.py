from __future__ import annotations


def build_welcome_text(first_name: str | None) -> str:
    name = first_name.strip() if first_name else "друг"

    return (
        f"Привет, {name}!\n\n"
        "лень - двигатель прогресса"
    )