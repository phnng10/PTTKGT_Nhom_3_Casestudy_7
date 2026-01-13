# PTTKGT_Nhom_3_Casestudy_7
Case study 7: Nhận diện văn bản đạo văn - Nhóm 3 - PTTKGT
Bước 1: Tạo môi trường ảo với Python (3.X.X)
     	py -m venv .venv
Bước 2: Kích hoạt môi trường ảo 
        .venv\Scripts\activate.ps1
Bước 3: Cài đặt các thư viện cần thiết
        pip install -r requirements.txt
Bước 4: Tiền xử lý văn bản và lưu vào file JSON
        python preprocess_text.py
Bước 5: So sánh văn bản và lưu vào file JSON
        python similarity_jaccard.py

hướng dẫn các triễn khai hàm ghi kết quả ở file similarity_metrics_advanced.py và utils.py
# đọc file + đo thời gian
(text1, t_read1) = measure_time(read_file, "text1.txt")
(text2, t_read2) = measure_time(read_file, "text2.txt")

read_success = True
time_read = t_read1 + t_read2

# giả sử words1, words2 đã có sau tiền xử lý
freq = word_frequency(words1)

# n-gram
(ngrams1, t_ng1) = measure_time(generate_ngrams, words1, 2)
(ngrams2, t_ng2) = measure_time(generate_ngrams, words2, 2)
ng_sim = ngram_similarity(words1, words2, 2)

# TF–IDF
(tf1, _) = measure_time(compute_tf, words1)
(tf2, _) = measure_time(compute_tf, words2)
(idf, _) = measure_time(compute_idf, [words1, words2])
(tfidf1, _) = measure_time(compute_tfidf, tf1, idf)
(tfidf2, _) = measure_time(compute_tfidf, tf2, idf)
tfidf_sim = tfidf_similarity(tfidf1, tfidf2)

time_tfidf = 0  # hoặc cộng thời gian chi tiết nếu cần

# ghi ra JSON
write_results_to_json(
    output_file="analysis_result.json",
    file1="text1.txt",
    file2="text2.txt",
    read_success=read_success,
    time_read=time_read,
    time_ngram=t_ng1 + t_ng2,
    time_tfidf=time_tfidf,
    word_freq=freq,
    n=2,
    ngrams1=ngrams1,
    ngrams2=ngrams2,
    ngram_sim=ng_sim,
    tf1=tf1,
    tf2=tf2,
    idf=idf,
    tfidf1=tfidf1,
    tfidf2=tfidf2,
    tfidf_sim=tfidf_sim
)
