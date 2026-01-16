import json
import logging
import unicodedata
import time
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chuẩn hóa Unicode - Kiểm tra kiểu dữ liệu , loại bỏ ký tự lạ như ký tự ẩn hoặc khoảng trắng.
def normalize_unicode(text):
    if not isinstance(text, str):
        text = str(text)
    text = unicodedata.normalize('NFC', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Cc')  # Loại bỏ control chars 
    return text.strip()

# Tính Edit Distance bằng quy hoạch động - Bao gồm thêm, xóa, thay thế ký tự.
def edit_distance_dp(str1, str2):
    str1 = normalize_unicode(str1)
    str2 = normalize_unicode(str2)
    
    if not str1:
        return len(str2)
    if not str2:
        return len(str1)
    
    # Đảm bảo str1 ngắn hơn 
    if len(str1) > len(str2):
        str1, str2 = str2, str1
    
    previous = list(range(len(str1) + 1))
    for i, c2 in enumerate(str2):
        current = [i + 1]
        for j, c1 in enumerate(str1):
            cost = 0 if c1 == c2 else 1
            current.append(min(
                previous[j + 1] + 1,      # Insert
                current[j] + 1,           # Delete
                previous[j] + cost        # Substitute
            ))
        previous = current
    
    return previous[-1]

# Chuyển đổi Edit Distance thành tỉ lệ giống nhau (0.0-1.0).
def edit_distance_to_similarity(edit_dist, len1, len2):
    if max(len1, len2) == 0:
        return 1.0
    return 1.0 - (edit_dist / max(len1, len2))

# Hàm chính xử lý Edit Distance - Validation, tính toán, logging, và xuất JSON.
def process_edit_distance(cleaned_words1, cleaned_words2, output_file='edit_distance_result.json'):
    start_time = time.time()
    logging.info("Bắt đầu xử lý Edit Distance.")
    
    warnings = []
    if not cleaned_words1 or len(cleaned_words1) < 5:
        warnings.append("text1: rỗng hoặc quá ngắn (<5 từ)")
    if not cleaned_words2 or len(cleaned_words2) < 5:
        warnings.append("text2: rỗng hoặc quá ngắn (<5 từ)")
    
    str1 = ' '.join(cleaned_words1)
    str2 = ' '.join(cleaned_words2)
    
    len1, len2 = len(str1), len(str2)
    logging.info(f"Độ dài chuỗi 1: {len1}, Chuỗi 2: {len2}")
    
    edit_dist = edit_distance_dp(str1, str2)
    logging.info(f"Edit Distance: {edit_dist}")
    
    similarity = edit_distance_to_similarity(edit_dist, len1, len2)
    logging.info(f"Tỉ lệ giống nhau: {similarity:.4f}")
    
    elapsed = time.time() - start_time
    
    result = {
        "strategy": "Edit Distance (Levenshtein DP)",
        "edit_distance": edit_dist,
        "similarity_ratio": round(similarity, 4),
        "similarity_percentage": f"{round(similarity * 100, 2)}%",
        "time_seconds": round(elapsed, 4),
        "details": {
            "len_str1": len1,
            "len_str2": len2,
            "str1_preview": str1[:100] + '...' if len(str1) > 100 else str1,  # Preview để debug
            "str2_preview": str2[:100] + '...' if len(str2) > 100 else str2,  # Preview để debug
            "warnings": warnings
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    logging.info(f"Kết quả lưu tại {output_file}")
    return result

# Đọc input từ JSON.
def load_input_from_json(input_file='preprocessed_data.json'):
    if not os.path.exists(input_file):
        logging.error(f"Không tìm thấy {input_file}. Chạy preprocess_text.py trước!")
        sys.exit(1)
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('text1', {}).get('cleaned_words', []), data.get('text2', {}).get('cleaned_words', [])

if __name__ == "__main__":
    cleaned1, cleaned2 = load_input_from_json()
    result = process_edit_distance(cleaned1, cleaned2)
    print(f"Edit Distance: {result['edit_distance']}")
    print(f"Tỉ lệ giống nhau: {result['similarity_percentage']}")
    if result['details']['warnings']:
        print("Cảnh báo:", result['details']['warnings'])