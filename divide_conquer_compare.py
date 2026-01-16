# Chiến lược Chia để trị: So sánh từng đoạn văn bản với tối ưu hiệu suất
import json
import time
import logging
import os
from typing import List, Dict

# Import các hàm similarity từ các thành viên khác
from similarity_jaccard import jaccard_similarity
from similarity_cosin import cosine_similarity, vectorize
from similarity_metrics_advanced import ngram_similarity, tfidf_similarity, compute_tfidf, compute_tf, compute_idf
from edit_distance_dp import edit_distance_to_similarity, edit_distance_dp  # từ TV5

# Fallback nếu TV2 chưa xong
from segmenter import segment_by_length
from preprocess_text import preprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cấu hình cải tiến
JACCARD_THRESHOLD = 0.15          # Ngưỡng pruning (có thể chỉnh để test)
METRIC_WEIGHTS = {
    "jaccard": 0.20,
    "cosine": 0.25,
    "ngram_bigram": 0.15,
    "edit_distance_similarity": 0.15,
    "tfidf": 0.25
}  # Tổng = 1.0

def load_segments(file_path: str = "segments.json") -> Dict:
    """Đọc segments từ file JSON (TV2), nếu không có thì tự tạo fallback"""
    if os.path.exists(file_path):
        logging.info(f"Đọc segments từ {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        logging.warning(f"Không tìm thấy {file_path}. Tự tạo segments...")
        data1 = preprocess("text1.txt")
        data2 = preprocess("text2.txt")
        segments1 = segment_by_length(data1['cleaned'], 50)
        segments2 = segment_by_length(data2['cleaned'], 50)
        return {"text1_segments": segments1, "text2_segments": segments2}

def compare_two_segments(seg1: List[str], seg2: List[str]) -> Dict:
    """So sánh 1 cặp đoạn với pruning + đo thời gian từng metric"""
    start_total = time.time()
    warnings = []
    if len(seg1) < 5:
        warnings.append("Đoạn 1 quá ngắn (<5 từ)")
    if len(seg2) < 5:
        warnings.append("Đoạn 2 quá ngắn (<5 từ)")

    str1 = ' '.join(seg1)
    str2 = ' '.join(seg2)

    # 1. Jaccard (nhanh, dùng để prune)
    start_j = time.time()
    jaccard = jaccard_similarity(seg1, seg2)
    time_j = time.time() - start_j

    scores = {
        "jaccard": round(jaccard, 4),
        "time_jaccard": round(time_j, 4)
    }

    # Pruning: Nếu Jaccard thấp → bỏ qua metric nặng
    pruned = False
    if jaccard < JACCARD_THRESHOLD:
        pruned = True
        logging.debug(f"Pruning: Jaccard {jaccard:.4f} < {JACCARD_THRESHOLD}")
        scores.update({
            "cosine": 0.0,
            "ngram_bigram": 0.0,
            "edit_distance_similarity": 0.0,
            "tfidf": 0.0,
            "time_cosine": 0.0,
            "time_ngram": 0.0,
            "time_edit": 0.0,
            "time_tfidf": 0.0
        })
    else:
        # Cosine
        start_c = time.time()
        vocab = list(set(seg1) | set(seg2))
        vec1 = vectorize(seg1, vocab)
        vec2 = vectorize(seg2, vocab)
        cosine = cosine_similarity(vec1, vec2)
        time_c = time.time() - start_c
        scores["cosine"] = round(cosine, 4)
        scores["time_cosine"] = round(time_c, 4)

        # N-gram
        start_n = time.time()
        ngram_sim = ngram_similarity(seg1, seg2, n=2)
        time_n = time.time() - start_n
        scores["ngram_bigram"] = round(ngram_sim, 4)
        scores["time_ngram"] = round(time_n, 4)

        # Edit Distance
        start_e = time.time()
        edit_dist = edit_distance_dp(str1, str2)
        edit_sim = edit_distance_to_similarity(edit_dist, len(str1), len(str2))
        time_e = time.time() - start_e
        scores["edit_distance_similarity"] = round(edit_sim, 4)
        scores["time_edit"] = round(time_e, 4)

        # TF-IDF
        start_t = time.time()
        tf1 = compute_tf(seg1)
        tf2 = compute_tf(seg2)
        idf = compute_idf([seg1, seg2])
        tfidf1 = compute_tfidf(tf1, idf)
        tfidf2 = compute_tfidf(tf2, idf)
        tfidf_sim = tfidf_similarity(tfidf1, tfidf2)
        time_t = time.time() - start_t
        scores["tfidf"] = round(tfidf_sim, 4)
        scores["time_tfidf"] = round(time_t, 4)

    total_time = time.time() - start_total
    return {
        **scores,
        "total_time": round(total_time, 4),
        "pruned": pruned,
        "warnings": warnings,
        "str1_preview": str1[:120] + '...' if len(str1) > 120 else str1,
        "str2_preview": str2[:120] + '...' if len(str2) > 120 else str2
    }

def divide_conquer_compare(segments1: List[List[str]], segments2: List[List[str]]) -> Dict:
    """Chiến lược chính với pruning và trọng số nâng cao"""
    start_time = time.time()
    logging.info("Bắt đầu Chia để trị (cải tiến pruning)...")

    if not segments1 or not segments2:
        logging.error("Segments rỗng.")
        return {"error": "Segments rỗng"}

    results = []
    total_weight = 0.0
    pruned_count = 0

    for i, seg1 in enumerate(segments1):
        for j, seg2 in enumerate(segments2):
            scores = compare_two_segments(seg1, seg2)

            # Trọng số: trung bình độ dài + TF-IDF (nếu không prune)
            seg_weight = (len(seg1) + len(seg2)) / 2
            tfidf_boost = scores.get("tfidf", 0.0) if not scores["pruned"] else 0.0
            weight = seg_weight + tfidf_boost
            total_weight += weight

            # Trung bình có trọng số các metric
            weighted_sum = sum(scores[k] * METRIC_WEIGHTS.get(k, 0.0) for k in METRIC_WEIGHTS)
            average_score = weighted_sum / sum(METRIC_WEIGHTS.values())

            if scores["pruned"]:
                pruned_count += 1

            results.append({
                "segment1_idx": i,
                "segment2_idx": j,
                "weight": round(weight, 2),
                "scores": {k: v for k, v in scores.items() if k not in ["warnings", "str1_preview", "str2_preview", "pruned"]},
                "average_score": round(average_score, 4),
                "pruned": scores["pruned"],
                "warnings": scores.get("warnings", []),
                "str1_preview": scores.get("str1_preview"),
                "str2_preview": scores.get("str2_preview")
            })

    # Tổng hợp cuối cùng
    weighted_sum_final = sum(r["weight"] * r["average_score"] for r in results)
    final_similarity = weighted_sum_final / total_weight if total_weight > 0 else 0.0

    elapsed = time.time() - start_time

    output = {
        "strategy": "Divide and Conquer (Pruning & Weighted)",
        "final_similarity": round(final_similarity, 4),
        "final_percentage": f"{round(final_similarity * 100, 2)}%",
        "execution_time_seconds": round(elapsed, 4),
        "total_pairs": len(results),
        "pruned_pairs": pruned_count,
        "pruning_threshold": JACCARD_THRESHOLD,
        "metric_weights": METRIC_WEIGHTS,
        "comparison_details": results
    }

    with open("divide_conquer_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    logging.info(f"Hoàn thành. Pruned {pruned_count}/{len(results)} cặp. Kết quả lưu tại divide_conquer_result.json")
    return output

if __name__ == "__main__":
    data = load_segments("segments.json")
    segments1 = data.get("text1_segments", [])
    segments2 = data.get("text2_segments", [])

    if not segments1 or not segments2:
        print("Không có đoạn nào. Kiểm tra segmenter.py hoặc segments.json")
        exit(1)

    result = divide_conquer_compare(segments1, segments2)

    print("\n=== KẾT QUẢ CHIA ĐỂ TRỊ (CẢI TIẾN) ===")
    print(f"Độ giống tổng thể: {result['final_percentage']}")
    print(f"Thời gian chạy: {result['execution_time_seconds']} giây")
    print(f"Tổng cặp so sánh: {result['total_pairs']}")
    print(f"Số cặp bị pruning: {result['pruned_pairs']} (ngưỡng Jaccard < {result['pruning_threshold']})")
