import requests
import wikipedia
from openai import OpenAI

# ================= Настройки =================
WEATHER_API_KEY = "14ebd344becc6b5f6d0c5da75f921119"
# =============================================
class AlphaAssistant:
    def __init__(self):
        # Клиент OpenAI удален
        pass

    def get_weather(self):
        """Запрос данных о погоде в Томске через API OpenWeatherMap"""
        city = "Tomsk,RU"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        
        try:
            res = requests.get(url).json()
            if res.get("cod") != 200:
                return "Не удалось получить данные о погоде."
            
            temp = round(res["main"]["temp"])
            status = res["weather"][0]["description"]
            return f"В Томске сейчас {temp} градусов, {status}."
        except:
            return "Ошибка связи с метеослужбой."

    def get_wiki(self, query):
        """Поиск краткого определения (1 предложение) в Википедии"""
        wikipedia.set_lang("ru")
        text = query.lower()
        prefixes = ["что такое", "кто такой", "википедия", "найди"]
        search_term = text
        for p in prefixes:
            search_term = search_term.replace(p, "")

        search_term = search_term.strip()

        if not search_term:
            return "Вы не уточнили, что именно нужно найти."

        print(f"[...] Ищу в Википедии: {search_term}")
        
        try:
            return wikipedia.summary(search_term.strip(), sentences=3)
        except wikipedia.DisambiguationError:
            return "Найдено слишком много совпадений. Уточните запрос."
        except wikipedia.PageError:
            return "Я не нашла такой статьи в Википедии."
        except:
            return "Ошибка при поиске в энциклопедии."

