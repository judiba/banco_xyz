class EmptyRagIndex:
    index_total = 0

    def search(self, question: str, k: int = 5):
        return []


def get_rag_docs_index():
    return EmptyRagIndex()
