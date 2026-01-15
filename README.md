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
