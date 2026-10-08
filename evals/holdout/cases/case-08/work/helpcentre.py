"""Rider help centre: riders can contribute tips, and the assistant answers from the articles."""

_ARTICLES = [{"title": "Unlocking a bike", "body": "Scan the code on the handlebar, then wait for the green light.", "by": "staff"}]


def add_article(rider, title, body):
    """Any signed-in rider can add a tip; it is searchable at once."""
    _ARTICLES.append({"title": title, "body": body, "by": rider})


def search(question, k=2):
    words = set(question.lower().split())
    scored = sorted(_ARTICLES, key=lambda a: -len(words & set((a["title"] + " " + a["body"]).lower().split())))
    return scored[:k]


def answer(llm, question):
    context = "\n".join(a["body"] for a in search(question))
    return llm("Answer the rider's question using only this help text.\n" + context + "\nQuestion: " + question)
