import unittest

from pydantic import ValidationError

from app.config.settings import Settings


class SettingsTests(unittest.TestCase):
    def test_environment_values_are_parsed(self) -> None:
        settings = Settings(
            _env_file=None,
            BOT_TOKEN="token",
            ADMIN_CHAT_IDS="-1001,-1002",
            LOG_LEVEL="warning",
        )
        self.assertEqual(settings.admin_chat_ids, [-1001, -1002])
        self.assertEqual(settings.log_level, "WARNING")

    def test_required_values_are_rejected(self) -> None:
        invalid_values = (
            {"BOT_TOKEN": "", "ADMIN_CHAT_IDS": "-1001"},
            {"BOT_TOKEN": "token", "ADMIN_CHAT_IDS": ""},
            {"BOT_TOKEN": "token", "ADMIN_CHAT_IDS": "-1001", "LOG_LEVEL": "verbose"},
        )
        for values in invalid_values:
            with self.subTest(values=values):
                with self.assertRaises(ValidationError):
                    Settings(_env_file=None, **values)


if __name__ == "__main__":
    unittest.main()
