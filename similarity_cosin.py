import math
from collections import Counter
import time


def vectorize(words, vocabulary):
    
    #Chuyển list từ thành vector tần suất
    count = Counter(words)
    return [count.get(word, 0) for word in vocabulary]


def cosine_similarity(vec1, vec2):
    
    #Tính Cosine Similarity giữa 2 vector
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def compare_segments_cosine(segments1, segments2):
    
    #So sánh từng đoạn của 2 văn bản
    results = []
    start = time.time()

    for i, seg1 in enumerate(segments1):
        for j, seg2 in enumerate(segments2):
            vocab = list(set(seg1) | set(seg2))
            vec1 = vectorize(seg1, vocab)
            vec2 = vectorize(seg2, vocab)

            score = cosine_similarity(vec1, vec2)

            results.append({
                "segment_1": i,
                "segment_2": j,
                "cosine_score": score
            })

    elapsed = time.time() - start

    return {
        "strategy": "Cosine Similarity (Segment-based)",
        "time_seconds": elapsed,
        "results": sorted(results, key=lambda x: x["cosine_score"], reverse=True)
    }


if __name__ == "__main__":
    from preprocess_text import preprocess
    from segmenter import segment_by_length

    print("Đang so sánh Cosine Similarity theo đoạn...")

    data1 = preprocess("text1.txt")
    data2 = preprocess("text2.txt")

    segments1 = segment_by_length(data1["cleaned"], 50)
    segments2 = segment_by_length(data2["cleaned"], 50)

    if not segments1 or not segments2:
        print("Không đủ dữ liệu để so sánh.")
        exit()

    result = compare_segments_cosine(segments1, segments2)

    print("Thời gian:", result["time_seconds"], "giây")
    print("Top 5 đoạn giống nhất:")

    for r in result["results"][:5]:
        print(
            f"Đoạn {r['segment_1']} - {r['segment_2']}: "
            f"Cosine = {r['cosine_score']:.4f}"
        )
