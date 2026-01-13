import re
import os
from underthesea import word_tokenize
import chardet

# Danh sách từ dừng tiếng Việt
STOPWORDS_VI = {'và', 'của', 'có', 'được', 'trong', 'là', 'với', 'để', 'cho', 'từ',
                'này', 'đó', 'các', 'những', 'một', 'không', 'như', 'khi', 'đã', 'sẽ',
                'bị', 'do', 'nên', 'nếu', 'mà', 'hay', 'hoặc', 'nhưng', 'vì', 'thì'}

# Danh sách từ dừng tiếng Anh
STOPWORDS_EN = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
                'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}

STOPWORDS = STOPWORDS_VI | STOPWORDS_EN

def detect_encoding(file_path):
    # Phát hiện encoding của file
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'

def read_file(file_path):
    # Kiểm tra file có tồn tại không
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
    
    # Kiểm tra file có rỗng không
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"File rỗng: {file_path}")
    
    encoding = detect_encoding(file_path)
    
    # Đọc file với encoding phù hợp
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

def clean_text(text):
    # Chuyển về chữ thường
    text = text.lower()
    # Bỏ ký tự đặc biệt
    text = re.sub(r'[^\w\s]', ' ', text)
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    # Tách từ (hỗ trợ tiếng Việt)
    try:
        words = word_tokenize(text, format="text").split()
        return words
    except:
        return text.split()

def remove_stopwords(words):
    # Loại bỏ stopwords
    return [w for w in words if w.lower() not in STOPWORDS]

def normalize_english(words):
    # Chuẩn hóa từ tiếng Anh: bỏ đuôi s, es, ing, ed
    result = []
    for word in words:
        if word.endswith('ing') and len(word) > 4:
            word = word[:-3]
        elif word.endswith('ed') and len(word) > 3:
            word = word[:-2]
        elif word.endswith('es') and len(word) > 3:
            word = word[:-2]
        elif word.endswith('s') and len(word) > 2:
            word = word[:-1]
        result.append(word)
    return result

def preprocess(file_path):
    # Hàm chính: tiền xử lý văn bản
    text = read_file(file_path)
    text = clean_text(text)
    words = tokenize(text)
    original_words = words.copy()
    words = remove_stopwords(words)
    words = normalize_english(words)
    
    return {
        'original': original_words,
        'cleaned': words,
        'original_count': len(original_words),
        'cleaned_count': len(words)
    }

import json

if __name__ == "__main__":
    # File input mẫu
    file1 = "text1.txt"
    file2 = "text2.txt"
    
    print(f"Đang xử lý {file1} và {file2}...")
    
    # Xử lý cả 2 file
    try:
        result1 = preprocess(file1)
        result2 = preprocess(file2)
        
        # Tạo data cho TV2, TV3...
        output_data = {
            "text1": {
                "cleaned_words": result1['cleaned'],
                "original_words": result1['original']
            },
            "text2": {
                "cleaned_words": result2['cleaned'],
                "original_words": result2['original']
            }
        }
        
        # Lưu ra file JSON
        with open("preprocessed_data.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print("\n--- Kết quả tiền xử lý ---")
        print(f"Đã lưu dữ liệu sạch vào 'preprocessed_data.json'")
        print(f"- Text 1: {result1['cleaned_count']} từ")
        print(f"- Text 2: {result2['cleaned_count']} từ")
        
    except Exception as e:
        print(f"Lỗi: {e}")

