import re

from rapidfuzz import fuzz, process

import Functions
import open_files_os

assistant = Functions.AlphaAssistant()

# Точные шаблоны. Порядок важен: сначала опасные и конкретные намерения.
PATTERNS = [
    ("cancel", r"отмен\w*"),
    ("system", r"(?:выключи|выруби|отруби|отключи)\s+(?:компьютер|комп|пк)"),
    ("wiki", r"что такое|кто такой|кто такая|расскажи (?:о|об|про)|найди информацию|википеди\w*"),
    ("weather", r"погод\w*|прогноз\w*|температур\w*|градус\w*|холодно|жарко"),
    ("mail", r"почт[аыуе]|письм\w*|проверь ящик|новые сообщения"),
    ("time", r"врем(?:я|ени)|который час|час(?:а|ов)?"),
    ("apps", r"открой|запусти|включи|поставь|покажи|пауз\w*|стоп|следующ\w*|предыдущ\w*|дальше|музык\w*"),
]
_COMPILED = [(name, re.compile(rf"(?<!\w)(?:{p})(?!\w)")) for name, p in PATTERNS]

# Запасной вариант на случай, если Vosk исказил слово («пагода»). Выключение сюда НЕ входит.
FUZZY_WORDS = {
    "weather": ["погода", "прогноз", "температура", "холодно"],
    "mail": ["почта", "письма", "сообщения"],
    "time": ["время", "времени"],
    "apps": ["открой", "запусти", "включи", "поставь", "покажи", "пауза", "следующий", "музыку"],
}
FUZZY_THRESHOLD = 82
EXIT_WORDS = {"пока", "выключись"}


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("ё", "е").split())


def is_exit_command(text: str) -> bool:
    """Выход по целому слову: «покажи» больше не содержит «пока»."""
    text = normalize(text)
    return bool(EXIT_WORDS & set(text.split())) or "до свидания" in text


def _pattern_intent(text: str):
    for name, rx in _COMPILED:
        if rx.search(text):
            return name
    return None


def _fuzzy_intent(text: str):
    best, best_score = None, 0
    for word in text.split():
        if len(word) < 4:
            continue
        for intent, keywords in FUZZY_WORDS.items():
            match = process.extractOne(word, keywords, scorer=fuzz.ratio)
            if match and match[1] > best_score:
                best, best_score = intent, match[1]
    return best if best_score >= FUZZY_THRESHOLD else None


def resolve_intent(text: str) -> str:
    text = normalize(text)
    intent = _pattern_intent(text) or _fuzzy_intent(text)

    if intent == "cancel":
        return open_files_os.cancel_shutdown()
    if intent == "system":
        return open_files_os.shutdown_pc()
    if intent == "wiki":
        return assistant.get_wiki(text)
    if intent == "weather":
        return assistant.get_weather()
    if intent == "mail":
        return open_files_os.check_mail()
    if intent == "time":
        return open_files_os.get_time()
    if intent == "apps":
        return open_files_os.run_app(text)

    return f"Я услышал: «{text}», но не понял команду. Повторите иначе."
