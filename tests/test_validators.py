import unittest

from app.domain.validators import is_valid_full_name, normalize_full_name


class ValidatorTests(unittest.TestCase):
    def test_full_name_is_normalized_and_validated(self) -> None:
        self.assertEqual(normalize_full_name("  Иванов   Иван   Иванович "), "Иванов Иван Иванович")
        self.assertTrue(is_valid_full_name("Иванов Иван Иванович"))

    def test_invalid_full_name_is_rejected(self) -> None:
        self.assertTrue(is_valid_full_name("Иванов Иван"))
        self.assertTrue(is_valid_full_name("John Smith"))
        self.assertTrue(is_valid_full_name("Иван"))
        self.assertTrue(is_valid_full_name("Анна-Мария O'Connor"))
        self.assertFalse(is_valid_full_name("123 456 789"))
        self.assertFalse(is_valid_full_name("Иванов Иван 1"))
        self.assertFalse(is_valid_full_name("Иванов @Иван"))
        self.assertFalse(is_valid_full_name(""))


if __name__ == "__main__":
    unittest.main()
