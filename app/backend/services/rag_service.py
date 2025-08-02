from backend.rag import build_rag_chain

rag_cache = {}

def build_rag_chain_cached(text: str):
    if text not in rag_cache:
        rag_cache[text] = build_rag_chain(text)
    return rag_cache[text]
