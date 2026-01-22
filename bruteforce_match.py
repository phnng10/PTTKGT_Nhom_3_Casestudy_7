from segmenter import segment_by_sentence
from difflib import SequenceMatcher
import time
import json

def sentence_similarity(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()

def brute_force_segment_match(segments1, segments2, threshold=0.6):
    matches = []

    for i, seg1 in enumerate(segments1):
        best_sim = 0.0
        best_j = -1

        for j, seg2 in enumerate(segments2):
            sim = sentence_similarity(seg1, seg2)
            if sim > best_sim:
                best_sim = sim
                best_j = j

        if best_sim >= threshold:
            matches.append((i, best_j, best_sim))

    return matches

def calculate_similarity(total_segments_text1, matched_segments):
    if total_segments_text1 == 0:
        return 0.0
    return matched_segments / total_segments_text1

def bruteforce_match(words1, words2, threshold=0.6):
    start_time = time.time()

    warnings = []
    if len(words1) < 5:
        warnings.append("Văn bản 1 quá ngắn (<5 từ)")
    if len(words2) < 5:
        warnings.append("Văn bản 2 quá ngắn (<5 từ)")

    text1 = " ".join(words1)
    text2 = " ".join(words2)

    segments1 = segment_by_sentence(text1, 3)
    segments2 = segment_by_sentence(text2, 3)

    segment_matches = brute_force_segment_match(
        segments1, segments2, threshold
    )

    similarity = calculate_similarity(
        len(segments1),
        len(segment_matches)
    )

    elapsed = time.time() - start_time

    result = {
        "strategy": "BruteForce",
        "similarity_score": round(similarity, 4),
        "time_seconds": round(elapsed, 4),
        "details": {
            "segments_text1": len(segments1),
            "segments_text2": len(segments2),
            "matched_segments": len(segment_matches),
            "threshold": threshold,
            "warnings": warnings,
            "top_segment_matches": [
                {
                    "segment1_idx": i,
                    "segment2_idx": j,
                    "similarity": round(sim, 4)
                }
                for i, j, sim in sorted(
                    segment_matches, key=lambda x: x[2], reverse=True
                )[:5]
            ]
        }
    }

    return result
if __name__ == "__main__":
    from preprocess_text import preprocess

    print("Đang chạy Bruteforce Matching...")

    data1 = preprocess("text1.txt", enable_logging=False)
    data2 = preprocess("text2.txt", enable_logging=False)

    words1 = data1["cleaned"]
    words2 = data2["cleaned"]

    result = bruteforce_match(words1, words2)

    with open("bruteforce_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        print("\n===== KẾT QUẢ SO KHỚP VĂN BẢN (BRUTE FORCE) =====")
        print(f"Độ giống nhau: {result[' similarity_score']:.3f}")
        print(f'Thời gian:{result['time_seconds']:.3f} giây")
        print(f"Tổng số đoạn của văn bản 1: {result['details']['segments_text1']}")
        print(f"Tổng số đoạn của văn bản 2: {result['details']['segments_text2']}")
        print(f"Số đoạn được đánh giá là tương đồng: {result['details']['matched_segments']}")

if result["details"]["warnings"]:
    print("\n Một số lưu ý trong quá trình so khớp:")
    for w in result["details"]["warnings"]:
        print(f"  - {w}")

print("\n 5 cặp đoạn có mức độ giống nhau cao nhất:")
for match in result["details"]["top_segment_matches"]:
    print(
        f"  Đoạn {match['segment1_idx']} (văn bản 1) "
        f"  Đoạn {match['segment2_idx']} (văn bản 2) "
        f" {match['similarity']:.3f}"
    )

    
        
