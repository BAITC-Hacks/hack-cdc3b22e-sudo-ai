"""Терминальный FAQ-бот без внешних зависимостей."""

import difflib
import re
from pathlib import Path


FAQ_PATH = Path(__file__).resolve().with_name("faq.txt")
UNKNOWN_ANSWER = "Не знаю"

STOP_WORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то",
    "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
    "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще", "нет",
    "о", "из", "ему", "теперь", "даже", "ну", "вдруг", "ли", "если", "уже", "или",
    "ни", "быть", "был", "него", "до", "вас", "нибудь", "опять", "уж", "вам",
    "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", "тут", "где",
    "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", "сам",
    "чтоб", "без", "будто", "чего", "раз", "тоже", "себе", "под", "будет", "ж",
    "тогда", "кто", "этот", "того", "потому", "этого", "какой", "какая", "какие",
    "какое", "совсем", "ним", "здесь", "этом", "почти", "мой", "тем", "чтобы",
    "нее", "сейчас", "были", "куда", "зачем", "всех", "никогда", "можно", "при",
    "наконец", "два", "об", "другой", "хоть", "после", "над", "больше", "тот",
    "через", "эти", "нас", "про", "всего", "них", "много", "разве", "три", "эту",
    "моя", "впрочем", "хорошо", "свою", "этой", "перед", "иногда", "лучше", "чуть",
    "том", "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между",
    "дела", "привет", "здравствуйте", "хакатон", "хакатоне", "хакатона", "сколько"
}

# Общие вопросительные слова с меньшим весом, чтобы предметные вопросы (например, «когда сдача») выбирали точный раздел
BROAD_WORDS = {"когда"}
EXIT_COMMANDS = {"exit", "quit", "q", "выход", "пока"}


def normalize(text: str) -> str:
    """Приведение к нижнему регистру и замена ё на е."""
    return text.casefold().replace("ё", "е")


def tokenize(text: str) -> list[str]:
    """Разбиение текста на слова (только буквы и цифры)."""
    return re.findall(r"[а-яa-z0-9]+", normalize(text))


def load_faq() -> list[tuple[str, str, list[str]]]:
    """
    Чтение FAQ. Поддерживает форматы:
    - 'вопрос | ответ' (ключевые слова берутся из вопроса)
    - 'вопрос | ответ | ключевые слова'
    """
    entries = []
    if not FAQ_PATH.exists():
        return entries

    for line in FAQ_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue

        question = parts[0]
        answer = parts[1]
        raw_keywords = parts[2].split() if len(parts) >= 3 else []

        # Автоматически обогащаем ключевые слова словами из вопроса
        question_words = [w for w in tokenize(question) if w not in STOP_WORDS]
        all_keywords = list(dict.fromkeys(raw_keywords + question_words))

        entries.append((question, answer, all_keywords))

    return entries


def match_word(word: str, keyword: str) -> bool:
    """Проверка совпадения слова с ключом (по префиксу или опечатке)."""
    if len(word) < 3 or len(keyword) < 3:
        return word == keyword

    if word.startswith(keyword) or keyword.startswith(word):
        return True

    # Допуск опечаток для слов от 5 символов
    if len(word) >= 5 and len(keyword) >= 5:
        if difflib.SequenceMatcher(None, word, keyword).ratio() >= 0.78:
            return True

    return False


def find_answer(question: str, entries: list[tuple[str, str, list[str]]]) -> str:
    all_tokens = tokenize(question)
    meaningful_words = [w for w in all_tokens if w not in STOP_WORDS]
    words_to_check = meaningful_words if meaningful_words else [w for w in all_tokens if w not in {"и", "в", "на", "с"}]

    if not words_to_check:
        return UNKNOWN_ANSWER

    best_answer = UNKNOWN_ANSWER
    best_score = 0.0

    for _, answer, keywords in entries:
        score = 0.0
        for w in words_to_check:
            for kw in keywords:
                if match_word(w, kw):
                    weight = 1.0 if kw in BROAD_WORDS else 2.0
                    score += weight
                    break

        if score > best_score:
            best_score = score
            best_answer = answer

    return best_answer if best_score >= 1.0 else UNKNOWN_ANSWER


def main():
    entries = load_faq()
    print("FAQ-бот хакатона готов к работе. Напишите вопрос или 'exit'/'выход' для завершения.")

    while True:
        try:
            raw_input = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nБот: До встречи!")
            break

        if not raw_input:
            continue

        if raw_input.casefold() in EXIT_COMMANDS:
            print("Бот: До встречи!")
            break

        print("Бот:", find_answer(raw_input, entries))


if __name__ == "__main__":
    main()

