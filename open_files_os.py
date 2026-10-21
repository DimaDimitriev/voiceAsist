import ctypes
import email
import imaplib
import os
import sys
from datetime import datetime
from email.header import decode_header, make_header

from rapidfuzz import fuzz, process

import config

IS_WINDOWS = sys.platform == "win32"

# Коды виртуальных клавиш Windows для управления медиа
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3

# Справочник программ
APPS = {
    "калькулятор": "calculator:",
    "блокнот": "notepad.exe",
    "браузер": "https://www.google.com",  # откроется браузер по умолчанию
    "ютуб": "https://www.youtube.com",
    "погода": "https://yandex.ru/pogoda",
    "музыку": "music:",
    "музыка": "music:",
    "эпл мьюзик": "music:",
    "яндекс музыка": "https://music.yandex.ru",
    "телеграмм": "tg:",
    "телеграм": "tg:",
    "параметры компьютера": "ms-settings:",
    "настройки": "ms-settings:",
    "часы": "ms-clock:",
    "холст": "ms-paint:",
    "фотографии": "ms-photos:",
    "календарь": "ms-calendar:",
}


def control_music(key_code):
    """Отправляет системное нажатие медиа-клавиши."""
    ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)


def handle_music_commands(command: str):
    """Обрабатывает команды управления воспроизведением."""
    if ("включи" in command or "поставь" in command) and ("любим" in command or "музык" in command):
        os.startfile("music:")  # открываем приложение (если закрыто) и жмём Play
        control_music(VK_MEDIA_PLAY_PAUSE)
        return "Включаю вашу музыку."

    if "пауз" in command or "стоп" in command:
        control_music(VK_MEDIA_PLAY_PAUSE)
        return "Ставлю музыку на паузу."

    if "следующ" in command or "дальше" in command:
        control_music(VK_MEDIA_NEXT_TRACK)
        return "Переключаю на следующий трек."

    if "предыдущ" in command:
        control_music(VK_MEDIA_PREV_TRACK)
        return "Возвращаюсь к предыдущему треку."

    return None


def _find_app(cmd: str):
    """Сначала точное вхождение названия, потом нечёткое сравнение по словам."""
    for name in sorted(APPS, key=len, reverse=True):
        if name in cmd:
            return name
    best, best_score = None, 0
    for word in (w for w in cmd.split() if len(w) > 3):
        match = process.extractOne(word, list(APPS), scorer=fuzz.ratio)
        if match and match[1] > best_score:
            best, best_score = match[0], match[1]
    return best if best_score >= 80 else None


def run_app(user_command: str):
    if not IS_WINDOWS:
        return "Запуск программ поддерживается только в Windows."

    cmd = user_command.lower()

    music_result = handle_music_commands(cmd)
    if music_result:
        return music_result

    app_name = _find_app(cmd)
    if app_name is None:
        return "Я не нашла такую программу в своём списке. Добавь её в APPS."
    try:
        # os.startfile работает как двойной клик и не блокирует скрипт
        os.startfile(APPS[app_name])
        return f"Окей, запускаю {app_name}."
    except Exception as e:
        return f"Не удалось запустить {app_name}. Ошибка: {e}"


def _decode_subject(raw_header) -> str:
    try:
        return str(make_header(decode_header(raw_header))) or "Без темы"
    except Exception:
        return "Без темы"


def check_mail():
    if not config.MAIL_USER or not config.MAIL_PASS:
        return "Почта не настроена. Добавьте MAIL_USER и MAIL_PASS в файл .env."

    mail = None
    try:
        mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, timeout=15)
        mail.login(config.MAIL_USER, config.MAIL_PASS)
        mail.select("INBOX", readonly=True)

        status, response = mail.search(None, "UNSEEN")
        if status != "OK":
            return "Не удалось получить список писем."

        unread_ids = response[0].split()
        count = len(unread_ids)
        if count == 0:
            return "Новых писем нет."

        subjects = []
        for mail_id in unread_ids[-3:][::-1]:
            _, msg_data = mail.fetch(mail_id, "(BODY.PEEK[HEADER.FIELDS (SUBJECT)])")
            msg = email.message_from_bytes(msg_data[0][1])
            subjects.append(_decode_subject(msg.get("Subject", "")))

        return f"У вас {count} новых писем. Последние темы: {', '.join(subjects)}."

    except imaplib.IMAP4.error:
        return "Не удалось войти в почту. Для mail.ru нужен пароль для внешнего приложения."
    except Exception as e:
        return f"Ошибка при проверке почты: {e}"
    finally:
        if mail:
            try:
                if mail.state == "SELECTED":
                    mail.close()
                mail.logout()
            except Exception:
                pass


def shutdown_pc():
    os.system("shutdown /s /t 15")
    return "Компьютер выключится через 15 секунд. Скажите «отмена», если передумали."


def cancel_shutdown():
    os.system("shutdown /a")
    return "Выключение отменено."


def get_time():
    return f"Сейчас {datetime.now().strftime('%H:%M')}"


if __name__ == "__main__":
    print(get_time())
    print(check_mail())
