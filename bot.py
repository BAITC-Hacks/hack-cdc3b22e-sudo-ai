"""Терминальный FAQ-бот без внешних зависимостей."""

import re
from pathlib import Path


FAQ_PATH = Path(__file__).resolve().with_name("faq.txt")
UNKNOWN_ANSWER = "Не знаю"


def load_faq():
    """Каждая строка: вопрос | ответ | начала ключевых слов через пробел."""
    entries = []
    for line in FAQ_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        question, answer, keywords = line.split("|", 2)
        entries.append((question.strip(), answer.strip(), keywords.split()))
    return entries


def find_answer(question, entries):
    text = question.casefold().replace("ё", "е")
    words = set(re.findall(r"[а-яa-z0-9]+", text))
    best_answer = UNKNOWN_ANSWER
    best_score = 0

    for _, answer, keywords in entries:
        # Считаем разные слова запроса, начинающиеся с одного из ключей.
        # Например, «наград» подходит к «награда», «награды» и «награду».
        score = sum(
            any(word.startswith(keyword) for keyword in keywords)
            for word in words
        )
        if score > best_score:
            best_score = score
            best_answer = answer

    return best_answer


def main():
    entries = load_faq()
    print("FAQ-бот хакатона. Введите вопрос или exit для выхода.")

    while True:
        try:
            question = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДо встречи!")
            break

        if question.casefold() == "exit":
            print("Бот: До встречи!")
            break

        print("Бот:", find_answer(question, entries))


if __name__ == "__main__":
    main()
