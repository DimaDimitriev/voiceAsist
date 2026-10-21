import voice
import user_frase_resolver as resolver


def main():
    voice.speak("Система активирована")

    while True:
        try:
            user_text = voice.listen().lower()
        except KeyboardInterrupt:
            break
        except OSError as e:  # нет микрофона / он занят
            print(f"Ошибка микрофона: {e}")
            break

        print(f"Распознано: {user_text}")

        if resolver.is_exit_command(user_text):
            final_message = "Голосовой ассистент закончил свою работу. До свидания!"
            voice.speak(final_message)
            break

        try:
            response = resolver.resolve_intent(user_text)
        except Exception as e:  # одна упавшая команда не должна ронять ассистента
            print(f"[!] Ошибка команды: {e}")
            response = "Не получилось выполнить команду."

        if response:
            voice.speak(response)

    print("Программа завершена.")


if __name__ == "__main__":
    main()
