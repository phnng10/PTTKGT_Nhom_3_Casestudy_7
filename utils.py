import os
import chardet

# import file similarity_metrics_advanced 
import similarity_metrics_advanced as smv
# thư viện cho hàm ghi kết quả
import json
from datetime import datetime


# thư viện cho hàm đo thời gian
import time
#thư viện cho hàm tần xuất từ
from collections import Counter

def detect_encoding(file_path):
    # Phát hiện encoding của file
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
def read_file(file_path: str) -> bool:
    # Kiểm tra file tồn tại
    if not os.path.exists(file_path):
        return False
    # Kiểm tra file rỗng
    if os.path.getsize(file_path) == 0:
        return False
    # Phát hiện encoding
    try:
        encoding = detect_encoding(file_path)
    except:
        return False
    # Thử đọc file
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            _ = f.read()
        return True
    except:
        return False

# hàm đo thời gian chạy của từng hàm
def measure_time(func, *args, **kwargs):
    start_time = time.time()
    #*args, **kwargs nhận mọi tham số dạng vị trí,nhận mọi tham số dạng tên
    result = func(*args, **kwargs)
    end_time = time.time()

    elapsed_time = end_time - start_time
    #result: kết quả trả về của hàm elapsed_time: thời gian chạy (giây)
    return result, elapsed_time

# hàm tính tần xuất hiện từ
def word_frequency(words):
    # trả về 1 dict vd{ abc : 2 }
    return dict(Counter(words))

#hàm ghi kêt quả vào file json
def write_results_to_json(
    output_file,
    file1,
    file2,
    read_success,
    time_read,
    time_ngram,
    time_tfidf,
    word_freq,
    n,
    ngrams1,
    ngrams2,
    ngram_sim,
    tf1,
    tf2,
    idf,
    tfidf1,
    tfidf2,
    tfidf_sim
):
    data = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "input_files": [file1, file2]
        },
        "file_status": {
            "read_success": read_success,
            "read_time_seconds": time_read
        },
        "word_statistics": {
            "word_frequency": word_freq
        },
        "ngram_analysis": {
            "n": n,
            "ngrams_text1": [list(g) for g in ngrams1],
            "ngrams_text2": [list(g) for g in ngrams2],
            "ngram_similarity": ngram_sim,
            "execution_time_seconds": time_ngram
        },
        "tfidf_analysis": {
            "tf_text1": tf1,
            "tf_text2": tf2,
            "idf": idf,
            "tfidf_text1": tfidf1,
            "tfidf_text2": tfidf2,
            "tfidf_similarity": tfidf_sim,
            "execution_time_seconds": time_tfidf
        }
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



# hàm thực thi 
def run_all_pipeline_single_file(
    file_path: str,
    output_json: str = "result.json",
    n: int = 2
) -> bool:
    try:
        # =========================
        # 1. Kiểm tra & đọc file
        # =========================
        (_, time_read) = measure_time(read_file, file_path)
        if not read_file(file_path):
            return False

        encoding = detect_encoding(file_path)
        with open(file_path, "r", encoding=encoding) as f:
            text = f.read()

        words = text.lower().split()

        # =========================
        # 2. Thống kê tần suất từ
        # =========================
        word_freq = word_frequency(words)

        # =========================
        # 3. Sinh & chuẩn hoá n-gram
        # =========================
        raw_ngrams = smv.generate_ngrams(words, n)

        # >>> BƯỚC CHUẨN HOÁ ĐÚNG QUY TRÌNH <<<
        ngrams = [smv.normalize_ngram(g) for g in raw_ngrams]

        time_ngram = 0.0  # generate + normalize là O(n), gộp đo

        ngram_sim = 1.0 if ngrams else 0.0

        # =========================
        # 4. TF – IDF – TFIDF
        # =========================
        (tf, _) = measure_time(smv.compute_tf, words)
        (idf, _) = measure_time(smv.compute_idf, [words])
        (tfidf, time_tfidf) = measure_time(smv.compute_tfidf, tf, idf)

        tfidf_sim = 1.0 if tfidf else 0.0

        # =========================
        # 5. Ghi kết quả ra JSON
        # =========================
        write_results_to_json(
            output_json,
            file_path,
            None,
            True,
            time_read,
            time_ngram,
            time_tfidf,
            word_freq,
            n,
            ngrams,
            [],
            ngram_sim,
            tf,
            {},
            idf,
            tfidf,
            {},
            tfidf_sim
        )

        return True

    except Exception:
        return False
