from collections import Counter
import time

def jaccard_similarity(words1, words2):
    # Tính độ tương đồng Jaccard
    if not words1 or not words2:
        return 0.0
    
    set1 = set(words1)
    set2 = set(words2)
    
    # Giao và hợp của 2 tập hợp
    intersection = set1 & set2
    union = set1 | set2
    
    # Công thức Jaccard: |A ∩ B| / |A ∪ B|
    return len(intersection) / len(union) if union else 0.0

def overlap_ratio(words1, words2):
    # Tính tỉ lệ trùng lặp
    if not words1 or not words2:
        return 0.0
    
    set1 = set(words1)
    set2 = set(words2)
    intersection = set1 & set2
    
    return len(intersection) / min(len(set1), len(set2))

def top_common_words(words1, words2, n=10):
    # Tìm top từ trùng nhiều nhất
    common = set(words1) & set(words2)
    if not common:
        return []
    
    # Đếm tần suất
    count1 = Counter(words1)
    count2 = Counter(words2)
    
    # Tổng tần suất của từ chung
    common_freq = {word: count1[word] + count2[word] for word in common}
    return sorted(common_freq.items(), key=lambda x: x[1], reverse=True)[:n]

def compare_jaccard(words1, words2):
    # Hàm chính: so sánh 2 văn bản
    start = time.time()
    
    # Validation: Kiểm tra rỗng hoặc quá ngắn
    warnings = []
    if not words1:
        warnings.append("Văn bản 1 rỗng")
    elif len(words1) < 5:
        warnings.append("Văn bản 1 quá ngắn (< 5 từ)")
        
    if not words2:
        warnings.append("Văn bản 2 rỗng")
    elif len(words2) < 5:
        warnings.append("Văn bản 2 quá ngắn (< 5 từ)")
    
    # Tính toán
    jaccard = jaccard_similarity(words1, words2)
    overlap = overlap_ratio(words1, words2)
    top_words = top_common_words(words1, words2, 10)
    
    elapsed = time.time() - start
    
    # Output theo format chuẩn
    result = {
        "strategy": "Jaccard Similarity",
        "similarity_score": jaccard,
        "time_seconds": elapsed,
        "details": {
            "overlap_ratio": overlap,
            "common_words": len(set(words1) & set(words2)),
            "top_common": top_words,
            "warnings": warnings  # Thêm cảnh báo vào output
        }
    }
    
    return result

import json
from preprocess_text import preprocess

if __name__ == "__main__":
    # 1. Lấy dữ liệu từ file đã tiền xử lý (hoặc chạy lại)
    try:
        print("Đang tính toán Jaccard Similarity...")
        
        # Cách 1: Chạy trực tiếp tiền xử lý
        data1 = preprocess("text1.txt")
        data2 = preprocess("text2.txt")
        words1 = data1['cleaned']
        words2 = data2['cleaned']
        
        # 2. Tính Jaccard
        result = compare_jaccard(words1, words2)
        
        # 3. Lưu kết quả cho TV7 (Khải Hân)
        with open("jaccard_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 4. In báo cáo
        print("Kết quả so sánh (Jaccard) ")
        print("Độ giống nhau:", result['similarity_score'])
        print("Overlap ratio:", result['details']['overlap_ratio'])
        print("Thời gian:", result['time_seconds'], "giây")
        print("Đã lưu kết quả vào 'jaccard_result.json'")
        
        print("Các từ trùng nhiều nhất:")
        for word, count in result['details']['top_common'][:5]:
            print(f"  - {word}: {count} lần")
            
        if result['details']['warnings']:
            print("\nLưu ý:")
            for w in result['details']['warnings']:
                print("-", w)

            
    except Exception as e:
        print(f"Lỗi: {e}")

