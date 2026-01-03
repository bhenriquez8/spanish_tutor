import unittest

from engine import (
    detect_tense,
    calculate_overlap,
    compare_translation,
    generate_feedback
)

class TestDetectTense(unittest.TestCase):

    def test_imperfect_regular(self):
        words = ["estaba", "caminando"]
        self.assertEqual(detect_tense(words), "imperfect")

    # TODO: re-adjust after figuring out accounting for accent marks
    def test_preterite_regular(self):
        words = ["camino", "a", "casa"]
        self.assertEqual(detect_tense(words), "unknown")

    def test_imperfect_irregular(self):
        words = ["era", "feliz"]
        self.assertEqual(detect_tense(words), "imperfect")

    def test_preterite_irregular(self):
        words = ["fue", "al", "parque"]
        self.assertEqual(detect_tense(words), "preterite")

    def test_unknown_tense(self):
        words = ["caminar", "es", "bueno"]
        self.assertEqual(detect_tense(words), "unknown")

class TestCompareTranslations(unittest.TestCase):

    def test_perfect_match(self):
        words = ["estaba", "caminando"]
        result = compare_translation(words, words, "imperfect", "imperfect")
        self.assertEqual(result, "perfect")

    # TODO: Change back after figuring out semantic equivalence
    def test_correct_different_phrasing(self):
        user = ["caminaba", "a", "tienda"]
        deepl = ["estaba", "caminando", "a", "la", "tienda"]
        result = compare_translation(user, deepl, "imperfect", "imperfect")
        self.assertEqual(result, "incorrect")

    def test_tense_mismatch(self):
        user = ["caminé", "a", "la", "tienda"]
        deepl = ["estaba", "caminando", "a", "la", "tienda"]
        result = compare_translation(user, deepl, "preterite", "imperfect")
        self.assertEqual(result, "tense_mismatch")

    def test_incorrect(self):
        user = ["perro", "azul"]
        deepl = ["estaba", "caminando"]
        result = compare_translation(user, deepl, "unknown", "imperfect")
        self.assertEqual(result, "incorrect")

class TestGenerateFeedback(unittest.TestCase):

    def test_perfect_feedback(self):
        msg = generate_feedback("perfect", "x", "imperfect")
        self.assertIn("Correct", msg)

    def test_tense_mismatch_feedback(self):
        msg = generate_feedback("tense_mismatch", "x", "imperfect")
        self.assertIn("imperfect", msg)

    def test_incorrect_feedback(self):
        translation = "Estaba caminando"
        msg = generate_feedback("incorrect", translation, "imperfect")
        self.assertIn(translation, msg)

