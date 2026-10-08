import unittest
import bot


class T(unittest.TestCase):
    def test_unknown_action_does_nothing(self):
        ran = []
        out = bot.handle(lambda p: '{"action": "format_disk"}', "my site is slow", run=lambda *a, **k: ran.append(a))
        self.assertEqual((out, ran), ("no action", []))

    def test_text_that_is_not_json_does_nothing(self):
        ran = []
        out = bot.handle(lambda p: "rm -rf / ; echo done", "x", run=lambda *a, **k: ran.append(a))
        self.assertEqual((out, ran), ("no action", []))

    def test_image_url_has_no_model_text(self):
        md = bot.status_markdown(7, "customer card 4111 1111 1111 1111 reset")
        self.assertNotIn("4111", md.split("badge.png")[1])


if __name__ == "__main__":
    unittest.main()
