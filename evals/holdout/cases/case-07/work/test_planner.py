import unittest
import planner


class T(unittest.TestCase):
    def setUp(self):
        planner._seen.clear()
        planner._all.clear()

    def test_a_model_that_never_stops_is_cut_off(self):
        calls = []
        llm = lambda m, max_tokens=None: calls.append(1) or {"tool": "t", "args": {}, "tokens": 10}
        r = planner.plan({"rider": "u1", "question": "q"}, llm, {"t": lambda: "x"})
        self.assertIn("error", r)
        self.assertLessEqual(len(calls), planner.MAX_TURNS)

    def test_an_anonymous_call_is_refused_before_any_model_call(self):
        calls = []
        r = planner.plan({"question": "q"}, lambda m, max_tokens=None: calls.append(1) or {"answer": "a", "tokens": 5}, {})
        self.assertEqual((r, calls), ({"error": "login required"}, []))

    def test_a_long_question_is_refused_before_any_model_call(self):
        calls = []
        r = planner.plan({"rider": "u2", "question": "x" * 5000}, lambda m, max_tokens=None: calls.append(1) or {"answer": "a", "tokens": 5}, {})
        self.assertEqual((r, calls), ({"error": "question not accepted"}, []))

    def test_the_per_rider_limit_applies(self):
        for _ in range(planner.MAX_REQUESTS_PER_HOUR):
            planner.plan({"rider": "u3", "question": "q"}, lambda m, max_tokens=None: {"answer": "a", "tokens": 5}, {}, now=lambda: 1000.0)
        self.assertEqual(planner.plan({"rider": "u3", "question": "q"}, lambda m, max_tokens=None: {"answer": "a", "tokens": 5}, {}, now=lambda: 1001.0), {"error": "rate limit"})

    def test_a_global_ceiling_applies_across_riders(self):
        planner.MAX_GLOBAL_PER_HOUR = 2
        try:
            for rider in ("g1", "g2"):
                planner.plan({"rider": rider, "question": "q"}, lambda m, max_tokens=None: {"answer": "a", "tokens": 5}, {}, now=lambda: 5000.0)
            self.assertEqual(planner.plan({"rider": "g3", "question": "q"}, lambda m, max_tokens=None: {"answer": "a", "tokens": 5}, {}, now=lambda: 5001.0), {"error": "busy"})
        finally:
            planner.MAX_GLOBAL_PER_HOUR = 2000

    def test_the_model_is_asked_for_no_more_than_the_remaining_budget(self):
        seen = []
        planner.plan({"rider": "u5", "question": "q"}, lambda m, max_tokens=None: seen.append(max_tokens) or {"answer": "a", "tokens": 5}, {})
        self.assertEqual(seen, [planner.MAX_TOKENS])

    def test_a_reply_without_a_token_count_or_an_answer_is_refused(self):
        self.assertEqual(planner.plan({"rider": "u6", "question": "q"}, lambda m, max_tokens=None: {"answer": "a"}, {}), {"error": "model reply carries no token count"})
        self.assertEqual(planner.plan({"rider": "u7", "question": "q"}, lambda m, max_tokens=None: {"tokens": 1}, {}), {"error": "model reply has no answer"})

    def test_a_missing_question_is_refused(self):
        self.assertEqual(planner.plan({"rider": "u8"}, lambda m, max_tokens=None: {"answer": "a", "tokens": 1}, {}), {"error": "question not accepted"})

    def test_a_normal_question_is_answered(self):
        self.assertEqual(planner.plan({"rider": "u4", "question": "q"}, lambda m, max_tokens=None: {"answer": "ride north", "tokens": 5}, {}), {"answer": "ride north"})


if __name__ == "__main__":
    unittest.main()
