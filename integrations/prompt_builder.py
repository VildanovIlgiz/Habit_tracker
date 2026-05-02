from __future__ import annotations


def build_habit_advice_prompt(habit_title: str, user_style: str = "neutral") -> str:
    style_instructions = {
        "neutral": "Ответь в нейтральном, поддерживающем тоне.",
        "friendly": "Ответь в дружелюбном, мотивирующем тоне, как хороший друг.",
        "strict": "Ответь строго и по делу, без лишних слов, как тренер.",
    }

    style_instruction = style_instructions.get(user_style, style_instructions["neutral"])

    return (
        f"Пользователь хочет закрепить привычку: «{habit_title}».\n\n"
        f"Дай один конкретный, практический совет, как легче придерживаться этой привычки. "
        f"Совет должен быть кратким (2-3 предложения).\n\n"
        f"{style_instruction}"
    )
