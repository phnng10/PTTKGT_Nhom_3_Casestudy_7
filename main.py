import os
import sys
import webbrowser

# Import các module xử lý và so sánh văn bản
from preprocess_text import preprocess
from similarity_jaccard import compare_jaccard
from similarity_cosin import compare_segments_cosine
from segmenter import segment_by_length
from bruteforce_match import bruteforce_match
from edit_distance_dp import process_edit_distance
from divide_conquer_compare import divide_conquer_compare
from report_builder import generate_html_report

# Kiểm tra file đầu vào
def validate_input(file1, file2):
    errors = []
    for f in [file1, file2]:
        if not os.path.exists(f):
            errors.append(f"File không tồn tại: {f}")
        elif os.path.getsize(f) == 0:
            errors.append(f"File rỗng: {f}")
        elif not f.endswith('.txt'):
            errors.append(f"File không phải .txt: {f}")
    return errors

# So sánh 2 file văn bản với tất cả chiến lược
def compare_texts(file1, file2):
    errors = validate_input(file1, file2)
    if errors:
        for e in errors:
            print(e)
        return None

    try:
        data1 = preprocess(file1, enable_logging=False)
        data2 = preprocess(file2, enable_logging=False)
    except Exception as e:
        print("Lỗi tiền xử lý:", e)
        return None

    words1 = data1["cleaned"]
    words2 = data2["cleaned"]

    results = []

    # === Jaccard ===
    try:
        jac = compare_jaccard(words1, words2)
        results.append({
            "strategy": jac["strategy"],
            "similarity_score": jac["similarity_score"],
            "time_seconds": jac["time_seconds"],
            "details": jac.get("details", {})
        })
    except:
        pass

    # === Cosin ===
    try:
        seg1 = segment_by_length(words1, 50)
        seg2 = segment_by_length(words2, 50)
        if seg1 and seg2:
            cos = compare_segments_cosine(seg1, seg2)
            best_score = cos["results"][0]["cosine_score"] if cos["results"] else 0
            results.append({
                "strategy": cos["strategy"],
                "similarity_score": best_score,
                "time_seconds": cos["time_seconds"],
                "details": {"top_matches": cos["results"][:5]}
            })
    except:
        pass

    # === Bruteforce ===
    try:
        bf = bruteforce_match(words1, words2, threshold=0.6)
        results.append({
            "strategy": bf["strategy"],
            "similarity_score": bf["similarity_score"],
            "time_seconds": bf["time_seconds"],
            "details": bf.get("details", {})
        })
    except Exception as e:
        print("Lỗi Bruteforce:", e)

    # === Edit Distance ===
    try:
        ed = process_edit_distance(words1, words2, output_file="__tmp_edit_main.json")
        results.append({
            "strategy": ed["strategy"],
            "similarity_score": ed["similarity_ratio"],
            "time_seconds": ed["time_seconds"],
            "details": ed.get("details", {})
        })
    except:
        pass

    # === Divide & Conquer ===
    try:
        if seg1 and seg2:
            dc = divide_conquer_compare(seg1, seg2)
            results.append({
                "strategy": dc["strategy"],
                "similarity_score": dc["final_similarity"],
                "time_seconds": dc["execution_time_seconds"],
                "details": {
                    "total_pairs": dc["total_pairs"],
                    "pruned_pairs": dc["pruned_pairs"]
                }
            })
    except:
        pass

    return results

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
    else:
        file1 = "text1.txt"
        file2 = "text2.txt"
        if not os.path.exists(file1) or not os.path.exists(file2):
            print("Cần có text1.txt và text2.txt hoặc truyền file khi chạy")
            sys.exit(1)

    results = compare_texts(file1, file2)

    if results:
        try:
            all_cases = [
                {
                    "case": f"So sánh {os.path.basename(file1)} vs {os.path.basename(file2)}",
                    "results": results
                }
            ]

            generate_html_report(all_cases)
            print("Báo cáo HTML: report.html")

            report_path = os.path.abspath("report.html")
            webbrowser.open("file://" + report_path)

        except Exception as e:
            print("Không tạo/mở được báo cáo:", e)
    else:
        print("Không có kết quả")