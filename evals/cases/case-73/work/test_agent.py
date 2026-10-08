import unittest
import agent


class T(unittest.TestCase):
    def test_a_model_that_never_stops_is_cut_off(self):
        calls = []
        llm = lambda m: calls.append(1) or {"tool": "t", "args": {}, "tokens": 10}
        r = agent.ask_endpoint({"user": "u1", "question": "q"}, llm, {"t": lambda: "x"})
        self.assertIn("error", r)
        self.assertLessEqual(len(calls), agent.MAX_TURNS)

    def test_anonymous_is_refused(self):
        self.assertEqual(agent.ask_endpoint({"question": "q"}, lambda m: {"answer": "a"}, {}), {"error": "login required"})

    def test_rate_limit(self):
        agent._seen.clear()
        ok = lambda m: {"answer": "a", "tokens": 1}
        res = [agent.ask_endpoint({"user": "u2", "question": "q"}, ok, {}) for _ in range(agent.MAX_REQUESTS_PER_HOUR + 1)]
        self.assertEqual(res[-1], {"error": "rate limit"})


if __name__ == "__main__":
    unittest.main()
