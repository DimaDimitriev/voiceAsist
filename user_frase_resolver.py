from rapidfuzz import fuzz, process
# import web     # Участник 3
import open_files_os
import Functions
# Словарь намерений
INTENTS = {
    'weather': ['погода', 'прогноз', 'температура', 'градусы', 'холодно'],
    'mail': ['почта', 'письма', 'проверь ящик', 'новые сообщения'],
    'apps': ['открой', 'запусти', 'включи'],
    'system':['выключи компьютер','отруби компьютер','выруби компьютер','отключи компьютер'],
    'time': ['время','час','времени'],
    'wiki': ['кто такой', 'что такое', 'расскажи о', 'найди информацию']
}
AlphaAssistant = Functions.AlphaAssistant()

def resolve_intent(text: str) -> str:
    best_intent = None
    max_score = 0

    for intent, keywords in INTENTS.items():
        result = process.extractOne(text, keywords, scorer=fuzz.WRatio)
        if result and result[1] > max_score:
            max_score = result[1]
            best_intent = intent
    #Порог уверенности
    if max_score < 70:
        return "Я услышал: '" + text + "', но не понял команду. Повторите иначе."

    #Погода
    if best_intent == 'weather':
        return AlphaAssistant.get_weather()

    #Поиск в википедии
    elif best_intent == 'wiki':
        # Вырезаем ключевые слова, чтобы оставить только запрос (н-р: "кто такой Пушкин")
        query = text
        for word in INTENTS['wiki']:
            query = query.replace(word, "").strip()
        return AlphaAssistant.get_wiki(query)

    #вывести последние несколько тем писем с почты
    elif best_intent == 'mail':
        return open_files_os.check_mail()

    #Включение всех приложений
    elif best_intent == 'apps':
        # Пытаемся понять, какое приложение запустить
        return open_files_os.run_app(text)

    #Выключение пк
    elif best_intent == 'system':
        return open_files_os.shutdown_pc()

    #Время
    elif best_intent == 'time':
        return open_files_os.get_time()

    else:
        return "Команда распознана, но обработчик еще не настроен."

# print(resolve_intent("что такое заяц беляк"))