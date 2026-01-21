import time
from segmenter import segment_by_sentence
from preprocess_text import preprocess
from difflib import SequenceMatcher


# Tính độ giống nhau giữa 2 câu
def sentence_similarity(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()


# So khớp toàn bộ đoạn
def brute_force_segment_match(segments1, segments2, threshold=0.6):
    matches = []

    for i in range(len(segments1)):
        for j in range(len(segments2)):
            sim = sentence_similarity(segments1[i], segments2[j])
            if sim >= threshold:
                matches.append((i, j, sim))

    return matches


# Tính % giống nhau
def calculate_similarity(total_segments, matched_segments):
    if total_segments == 0:
        return 0
    return matched_segments / total_segments * 100


def run_brute_force_match(text1_path, text2_path):
    start_time = time.time()

    data1 = preprocess(text1_path)
    data2 = preprocess(text2_path)

    text1 = data1["clean_text"]
    text2 = data2["clean_text"]

    segments1 = segment_by_sentence(text1, 3)
    segments2 = segment_by_sentence(text2, 3)

    matches = brute_force_segment_match(segments1, segments2)

    total_segments = len(segments1) + len(segments2)
    matched_segments_1 = set(i for i, _, _ in matches)
    matched_segments_2 = set(j for _, j, _ in matches)

    matched_unique = len(matched_segments_1) + len(matched_segments_2)
    similarity = matched_unique / total_segments * 100

    elapsed_time = time.time() - start_time

    return {
        "strategy": "Brute Force Match",
        "similarity_score": similarity,
        "time_seconds": elapsed_time,
        "details": {
            "matched_pairs": len(matches)
        }
    }


if __name__ == "__main__":
    result = run_brute_force_match("text1.txt", "text2.txt")
    print(result)

