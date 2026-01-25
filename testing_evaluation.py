import os
import json

# Import các module xử lý và so sánh văn bản
from preprocess_text import preprocess
from similarity_jaccard import compare_jaccard
from similarity_cosin import compare_segments_cosine
from segmenter import segment_by_length
from bruteforce_match import bruteforce_match
from edit_distance_dp import process_edit_distance
from divide_conquer_compare import divide_conquer_compare

# Thư mục chứa các test case
TEST_DIR = "tests"

# Thư mục lưu kết quả đánh giá
OUTPUT_DIR = "evaluation_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

def run_one_case(case_name, case_path, expected_similarity=None):
    """
    Chạy một test case:
    - Đọc 2 file văn bản
    - Tiền xử lý
    - So sánh bằng nhiều chiến lược khác nhau
    - Lưu kết quả ra file JSON
    """
    print(f"\nĐang chạy case: {case_name}")

    # Đường dẫn tới 2 file văn bản cần so sánh
    text1_path = os.path.join(case_path, "text1.txt")
    text2_path = os.path.join(case_path, "text2.txt")

    # Tiền xử lý văn bản (làm sạch, tách từ, chuẩn hóa,…)
    data1 = preprocess(text1_path)
    data2 = preprocess(text2_path)

    # Lấy danh sách từ sau khi đã làm sạch
    words1 = data1["cleaned"]
    words2 = data2["cleaned"]

    results = []  # Lưu kết quả của từng phương pháp so sánh

    # === So sánh bằng Jaccard ===
    raw = compare_jaccard(words1, words2)
    results.append({
        "strategy": raw["strategy"],
        "similarity_score": raw["similarity_score"],
        "time_seconds": raw["time_seconds"],
        "details": raw.get("details", {})
    })

    # === Chia văn bản thành các đoạn ===
    # Mỗi đoạn gồm 50 từ
    seg1 = segment_by_length(words1, 50)
    seg2 = segment_by_length(words2, 50)

    # ==== So sánh Cosine theo từng đoạn ====
    if seg1 and seg2:
        raw = compare_segments_cosine(seg1, seg2)

        # Lấy điểm cosin cao nhất trong các cặp đoạn
        best_score = raw["results"][0]["cosine_score"] if raw["results"] else 0

        results.append({
            "strategy": raw["strategy"],
            "similarity_score": best_score,
            "time_seconds": raw["time_seconds"],
            "details": {
                "top_matches": raw["results"][:5]  # Chỉ lấy top 5 cặp giống nhất
            }
        })

    # === So sánh bằng Brute Force ===
    raw = bruteforce_match(words1, words2, threshold=0.6)
    results.append({
        "strategy": raw["strategy"],
        "similarity_score": raw["similarity_score"],
        "time_seconds": raw["time_seconds"],
        "details": raw.get("details", {})
    })

    # === So sánh bằng Edit Distance (DP) ===
    raw = process_edit_distance(words1, words2, output_file="__tmp_edit.json")
    results.append({
        "strategy": raw["strategy"],
        "similarity_score": raw["similarity_ratio"],
        "time_seconds": raw["time_seconds"],
        "details": raw.get("details", {})
    })

    # ==== So sánh theo Divide & Conquer ===
    if seg1 and seg2:
        raw = divide_conquer_compare(seg1, seg2)
        results.append({
            "strategy": raw["strategy"],
            "similarity_score": raw["final_similarity"],
            "time_seconds": raw["execution_time_seconds"],
            "details": {
                "total_pairs": raw["total_pairs"],     # Tổng số cặp đoạn
                "pruned_pairs": raw["pruned_pairs"]    # Số cặp bị loại bỏ
            }
        })

    # Tổng hợp kết quả của test case
    output = {
        "case": case_name,
        "expected_similarity": expected_similarity,
        "results": results
    }

    # Ghi kết quả ra file JSON
    out_file = os.path.join(OUTPUT_DIR, f"evaluation_{case_name}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Đã lưu kết quả: {out_file}")


def run_all_tests():
    """
    Chạy toàn bộ test case trong thư mục tests
    """
    for case_name in os.listdir(TEST_DIR):
        case_path = os.path.join(TEST_DIR, case_name)

        # Bỏ qua nếu không phải thư mục
        if not os.path.isdir(case_path):
            continue

        # Đọc độ tương đồng mong đợi (nếu có)
        expected_file = os.path.join(case_path, "expected.txt")
        expected_similarity = None
        if os.path.exists(expected_file):
            with open(expected_file, "r") as f:
                try:
                    expected_similarity = float(f.read().strip())
                except:
                    expected_similarity = None

        run_one_case(case_name, case_path, expected_similarity)


# === Chương trình chính ===
if __name__ == "__main__":
    print("Bắt đầu chạy toàn bộ bộ test...")
    run_all_tests()
    print("\nDữ liệu đã nằm trong thư mục evaluation_results")
