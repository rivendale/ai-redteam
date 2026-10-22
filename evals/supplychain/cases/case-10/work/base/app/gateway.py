from llm_router import Router

router = Router(base_url="https://api.llm-router.example/v1")


def ask(prompt: str) -> str:
    return router.complete(model="general", prompt=prompt)
