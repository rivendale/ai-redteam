"""Question answering over the company's documents. One shared index serves every customer; every query is filtered by tenant inside the query."""
from store import Store

index = Store()


def ingest(tenant, doc_id, vec, text):
    index.add(doc_id, vec, text, tenant=tenant)


def delete(tenant, doc_id):
    """Deleting removes the tenant's document, text and vector, from the index at once."""
    index.rows[:] = [r for r in index.rows if not (r["id"] == doc_id and r["tenant"] == tenant)]


def answer(llm, embed, tenant, question):
    hits = index.query(embed(question), top_k=3, where={"tenant": tenant})
    context = "\n".join(h["text"] for h in hits)
    return llm("Answer from this context only.\n" + context + "\nQuestion: " + question)
