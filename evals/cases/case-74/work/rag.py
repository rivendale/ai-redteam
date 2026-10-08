"""Question answering over the company's documents. One shared index serves every customer."""
from store import Store

index = Store()


def ingest(tenant, doc_id, vec, text):
    index.add(doc_id, vec, text, tenant=tenant, deleted=False)


def delete(doc_id):
    """Deleting marks the document; it is removed from the index by the nightly job."""
    for r in index.rows:
        if r["id"] == doc_id:
            r["deleted"] = True


def answer(llm, embed, tenant, question):
    hits = index.query(embed(question), top_k=3)
    context = "\n".join(h["text"] for h in hits)
    return llm("Answer from this context only.\n" + context + "\nQuestion: " + question)
