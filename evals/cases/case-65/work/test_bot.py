import subprocess
import unittest
import bot


def fake(out="", code=0):
    return lambda *a, **k: subprocess.CompletedProcess(a, code, stdout=out, stderr="")


class T(unittest.TestCase):
    def test_unknown_action_does_nothing(self):
        ran = []
        out = bot.handle(lambda p: '{"action": "format_disk"}', 7, "my site is slow", lambda *a, **k: ran.append(a), None)
        self.assertEqual((out, ran), ("no action", []))

    def test_text_that_is_not_json_does_nothing(self):
        ran = []
        out = bot.handle(lambda p: "rm -rf / ; echo done", 7, "x", lambda *a, **k: ran.append(a), None)
        self.assertEqual((out, ran), ("no action", []))

    def test_image_url_has_no_model_text(self):
        md = bot.status_markdown(7, "customer card 4111 1111 1111 1111 reset")
        self.assertNotIn("4111", md.split("badge.png")[1])

    def test_a_change_waits_for_staff_with_the_ticket_id(self):
        asked, ran = [], []
        out = bot.handle(lambda p: '{"action": "restart_web"}', 7, "down", lambda *a, **k: ran.append(a), lambda t, a: asked.append((t, a)))
        self.assertEqual((out, asked, ran), ("queued for staff approval", [(7, "restart_web")], []))

    def test_a_stopped_service_is_reported_not_failed(self):
        out = bot.handle(lambda p: '{"action": "web_status"}', 7, "down", fake("inactive\n", 3), None)
        self.assertEqual(out, "web service: inactive")

    def test_command_output_is_not_posted_as_it_is(self):
        out = bot.handle(lambda p: '{"action": "cache_stats"}', 7, "slow", fake("12M\t/var/cache/app\nsecret-line\n"), None)
        self.assertEqual(out, "cache size: 12M")


if __name__ == "__main__":
    unittest.main()
