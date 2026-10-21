"""Проверка разбора команд без микрофона и без побочных действий: python -m unittest"""
import unittest
from unittest.mock import patch

import open_files_os
import user_frase_resolver as r


class ResolverTest(unittest.TestCase):
    def check(self, phrase, target, expected):
        with patch.object(target[0], target[1], return_value="OK") as m:
            self.assertEqual(r.resolve_intent(phrase), "OK", phrase)
            m.assert_called_once()
            if expected is not None:
                self.assertIn(expected, str(m.call_args))

    def test_weather(self):
        self.check("какая сегодня погода", (r.assistant, "get_weather"), None)
        self.check("пагода", (r.assistant, "get_weather"), None)  # искажённое слово

    def test_time_mail_system(self):
        self.check("сколько сейчас времени", (open_files_os, "get_time"), None)
        self.check("проверь почту", (open_files_os, "check_mail"), None)
        self.check("выключи компьютер", (open_files_os, "shutdown_pc"), None)
        self.check("отмена", (open_files_os, "cancel_shutdown"), None)

    def test_wiki(self):
        self.check("что такое заяц беляк", (r.assistant, "get_wiki"), "заяц беляк")

    def test_apps_and_music(self):
        self.check("открой калькулятор", (open_files_os, "run_app"), "калькулятор")
        self.check("пауза", (open_files_os, "run_app"), "пауза")
        self.check("следующий трек", (open_files_os, "run_app"), "следующий")
        self.check("покажи фотографии", (open_files_os, "run_app"), "фотографии")

    def test_unknown(self):
        self.assertIn("не понял", r.resolve_intent("бла бла квантовый банан"))

    def test_exit(self):
        self.assertTrue(r.is_exit_command("пока"))
        self.assertTrue(r.is_exit_command("выключись"))
        self.assertTrue(r.is_exit_command("ну все до свидания"))
        self.assertFalse(r.is_exit_command("покажи фотографии"))
        self.assertFalse(r.is_exit_command("выключи компьютер"))


if __name__ == "__main__":
    unittest.main()
