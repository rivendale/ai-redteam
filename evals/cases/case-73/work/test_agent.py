import unittest
import agent


class T(unittest.TestCase):
    def test_a_model_that_never_stops_is_cut_off(self):
        calls = []
        llm = lambda m: calls.append(1) or {"tool": "t", "args": {}, "tokens": 10}
        r = agent.ask_endpoint({"user": "u1", "question": "q"}, llm, {"t": lambda: "x"})
        self.assertIn("error", r)
        self.assertLessEqual(len(calls), agent.MAX_TURNS)

    def test_an_oversized_question_is_refused_before_any_model_call(self):
        calls = []
        r = agent.ask_endpoint({"user": "u3", "question": "x" * 100000}, lambda m: calls.append(1) or {"answer": "a"}, {})
        self.assertEqual((r, calls), ({"error": "question too long"}, []))

    def test_a_question_that_is_not_text_is_refused_before_any_model_call(self):
        calls = []
        r = agent.ask_endpoint({"user": "u4", "question": ["x" * 100000]}, lambda m: calls.append(1) or {"answer": "a"}, {})
        self.assertEqual((r, calls), ({"error": "question must be text"}, []))

    def test_a_huge_tool_result_is_truncated(self):
        seen = []
        replies = iter([{"tool": "t", "args": {}, "tokens": 1}, {"answer": "done", "tokens": 1}])
        llm = lambda m: seen.append(m) or next(replies)
        agent.ask_endpoint({"user": "u4", "question": "q"}, llm, {"t": lambda: "y" * 100000})
        self.assertLessEqual(len(seen[1][-1]["content"]), agent.MAX_TOOL_RESULT_CHARS)

    def test_anonymous_is_refused(self):
        self.assertEqual(agent.ask_endpoint({"question": "q"}, lambda m: {"answer": "a"}, {}), {"error": "login required"})

    def test_rate_limit(self):
        agent._seen.clear()
        ok = lambda m: {"answer": "a", "tokens": 1}
        res = [agent.ask_endpoint({"user": "u2", "question": "q"}, ok, {}) for _ in range(agent.MAX_REQUESTS_PER_HOUR + 1)]
        self.assertEqual(res[-1], {"error": "rate limit"})


if __name__ == "__main__":
    unittest.main()
