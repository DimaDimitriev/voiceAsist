import requests
import wikipedia

import config

wikipedia.set_lang("ru")

# Длинные фразы идут первыми, чтобы «найди информацию о» не обрезалось до «найди»
_WIKI_PREFIXES = sorted(
    ["что такое", "кто такой", "кто такая", "расскажи о", "расскажи об", "расскажи про",
     "найди информацию о", "найди информацию", "википедия", "найди"],
    key=len, reverse=True,
)


class AlphaAssistant:
    def get_weather(self) -> str:
        """Погода через OpenWeatherMap (город и ключ задаются в .env)."""
        if not config.WEATHER_API_KEY:
            return "Не задан ключ погоды. Добавьте WEATHER_API_KEY в файл .env."
        try:
            res = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": config.WEATHER_CITY, "appid": config.WEATHER_API_KEY,
                        "units": "metric", "lang": "ru"},
                timeout=5,
            ).json()
            if str(res.get("cod")) != "200":
                return "Не удалось получить данные о погоде."
            temp = round(res["main"]["temp"])
            status = res["weather"][0]["description"]
            return f"Сейчас {temp} градусов, {status}."
        except Exception:
            return "Ошибка связи с метеослужбой."

    @staticmethod
    def _clean_query(text: str) -> str:
        text = text.lower()
        for prefix in _WIKI_PREFIXES:
            idx = text.find(prefix)
            if idx != -1:
                text = text[idx + len(prefix):]
                break
        return text.strip()

    def get_wiki(self, query: str) -> str:
        """Краткая справка из Википедии (2 предложения)."""
        term = self._clean_query(query)
        if not term:
            return "Вы не уточнили, что именно нужно найти."

        print(f"[...] Ищу в Википедии: {term}")
        try:
            return wikipedia.summary(term, sentences=2)
        except wikipedia.DisambiguationError as e:
            try:  # берём первый вариант вместо отказа
                return wikipedia.summary(e.options[0], sentences=2)
            except Exception:
                return "Найдено слишком много совпадений. Уточните запрос."
        except wikipedia.PageError:
            return "Я не нашла такой статьи в Википедии."
        except Exception:
            return "Ошибка при поиске в энциклопедии."
