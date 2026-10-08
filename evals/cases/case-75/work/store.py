"""A tiny in-memory vector store (stand-in for the real one): rows are dicts with a vector and metadata."""


class Store:
    def __init__(self):
        self.rows = []

    def add(self, doc_id, vec, text, **meta):
        self.rows.append({"id": doc_id, "vec": vec, "text": text, **meta})

    def query(self, vec, top_k=3, where=None):
        def dot(a, b):
            return sum(x * y for x, y in zip(a, b))
        rows = [r for r in self.rows if all(r.get(k) == v for k, v in (where or {}).items())]
        return sorted(rows, key=lambda r: -dot(vec, r["vec"]))[:top_k]
