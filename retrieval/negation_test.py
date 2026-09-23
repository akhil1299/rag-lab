# The negation test: proves that embeddings cannot distinguish between
# a statement and its negation, since almost all the words are
# identical and only one word ("not") flips the entire meaning.

import numpy as np
from retrieval.embed import embed_text

SENTENCE_A = "This account is approved for options trading"
SENTENCE_B = "This account is NOT approved for options trading"


def cosine_similarity(vec_a, vec_b):
    """
    Returns the cosine similarity between two vectors: a number from
    -1 (opposite) to 1 (identical), measuring how similar their
    *direction* is, ignoring magnitude.
    """
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    return dot_product / (norm_a * norm_b)


if __name__ == "__main__":
    embedding_a = embed_text(SENTENCE_A)
    embedding_b = embed_text(SENTENCE_B)

    similarity = cosine_similarity(embedding_a, embedding_b)

    print(f"Sentence A: {SENTENCE_A}")
    print(f"Sentence B: {SENTENCE_B}")
    print(f"Cosine similarity: {similarity:.4f}")