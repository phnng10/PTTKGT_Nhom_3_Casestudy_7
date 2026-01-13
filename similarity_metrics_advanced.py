import re
import math

def generate_ngrams(words, n):
    """
    Sinh danh sách n-gram từ danh sách từ
    :param words: list[str] danh sách từ đã clean
    :param n: số lượng từ trong mỗi n-gram
    :return: list[tuple]
    """
    return [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]

def normalize_ngram(ngram):
    """
    Chuẩn hoá một n-gram
    """
    return tuple(
        re.sub(r'[^\w\s]', '', word.lower())
        for word in ngram
    )


def ngram_similarity(words1, words2, n=2):
    g1 = set(generate_ngrams(words1, n))
    g2 = set(generate_ngrams(words2, n))

    if not g1 or not g2:
        return 0.0

    return len(g1 & g2) / len(g1 | g2)


def compute_tf(words):
    tf = {}
    total = len(words)
    for w in words:
        tf[w] = tf.get(w, 0) + 1
    return {w: c / total for w, c in tf.items()}


def compute_idf(documents):
    """
    documents: list[list[str]]
    """
    N = len(documents)
    idf = {}
    vocab = set(word for doc in documents for word in doc)

    for word in vocab:
        df = sum(1 for doc in documents if word in doc)
        idf[word] = math.log(N / (df + 1))
    return idf


def compute_tfidf(tf, idf):
    return {w: tf[w] * idf.get(w, 0) for w in tf}


def tfidf_similarity(tfidf1, tfidf2):
    score = 0.0
    for w in tfidf1:
        score += tfidf1[w] * tfidf2.get(w, 0)
    return score
