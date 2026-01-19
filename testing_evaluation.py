# testing_evaluation.py
# File này dùng để:
# - Duyệt các bộ test trong thư mục tests/
# - Chạy từng chiến lược so sánh
# - Ép kết quả về chung 1 format
# - Lưu ra file JSON để phân tích tiếp

import os
import json

from preprocess_text import preprocess
from similarity_jaccard import compare_jaccard
from similarity_cosin import compare_segments_cosine
from segmenter import segment_by_length
from edit_distance_dp import process_edit_distance
from divide_conquer_compare import divide_conquer_compare

TEST_DIR = "tests"
OUTPUT_DIR = "evaluation_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Chạy 1 bộ test
def run_one_case(case_name, case_path, expected_similarity=None):
    print(f"\nĐang chạy case: {case_name}")

    text1_path = os.path.join(case_path, "text1.txt")
    text2_path = os.path.join(case_path, "text2.txt")

    # Tiền xử lý 2 văn bản
    data1 = preprocess(text1_path)
    data2 = preprocess(text2_path)

    words1 = data1["cleaned"]
    words2 = data2["cleaned"]

    results = []

    # ===== 1. Jaccard =====
    raw = compare_jaccard(words1, words2)
    results.append({
        "strategy": raw["strategy"],
        "similarity_score": raw["similarity_score"],
        "time_seconds": raw["time_seconds"],
        "details": raw.get("details", {})
    })

    # ===== 2. Cosine theo đoạn =====
    seg1 = segment_by_length(words1, 50)
    seg2 = segment_by_length(words2, 50)

    if seg1 and seg2:
        raw = compare_segments_cosine(seg1, seg2)
        best_score = raw["results"][0]["cosine_score"] if raw["results"] else 0

        results.append({
            "strategy": raw["strategy"],
            "similarity_score": best_score,
            "time_seconds": raw["time_seconds"],
            "details": {
                "top_matches": raw["results"][:5]
            }
        })

    # ===== 3. Edit Distance =====
    raw = process_edit_distance(words1, words2, output_file="__tmp_edit.json")
    results.append({
        "strategy": raw["strategy"],
        "similarity_score": raw["similarity_ratio"],
        "time_seconds": raw["time_seconds"],
        "details": raw.get("details", {})
    })

    # ===== 4. Divide & Conquer =====
    if seg1 and seg2:
        raw = divide_conquer_compare(seg1, seg2)
        results.append({
            "strategy": raw["strategy"],
            "similarity_score": raw["final_similarity"],
            "time_seconds": raw["execution_time_seconds"],
            "details": {
                "total_pairs": raw["total_pairs"],
                "pruned_pairs": raw["pruned_pairs"]
            }
        })

    # Gộp kết quả của 1 case
    output = {
        "case": case_name,
        "expected_similarity": expected_similarity,
        "results": results
    }

    # Lưu ra file
    out_file = os.path.join(OUTPUT_DIR, f"evaluation_{case_name}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Đã lưu kết quả: {out_file}")


# Chạy tất cả các bộ test
def run_all_tests():
    for case_name in os.listdir(TEST_DIR):
        case_path = os.path.join(TEST_DIR, case_name)

        # Bỏ qua nếu không phải folder
        if not os.path.isdir(case_path):
            continue

        # Nếu có file expected.txt thì đọc độ giống mong muốn
        expected_file = os.path.join(case_path, "expected.txt")
        expected_similarity = None
        if os.path.exists(expected_file):
            with open(expected_file, "r") as f:
                try:
                    expected_similarity = float(f.read().strip())
                except:
                    expected_similarity = None

        run_one_case(case_name, case_path, expected_similarity)


# Chạy chương trình
if __name__ == "__main__":
    print("Bắt đầu chạy toàn bộ bộ test...")
    run_all_tests()
    print("\nXong hết rồi, dữ liệu đã nằm trong thư mục evaluation_results 🎯")
