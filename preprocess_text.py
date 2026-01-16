import re
import os
from underthesea import word_tokenize
import chardet
import logging

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
    # Bỏ ký tự đặc biệt (nhưng giữ lại dấu câu . ! ?)
    text = re.sub(r'[^\w\s.!?]', ' ', text)
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_text_for_segmenter(text):
    # Giữ nguyên text gốc với dấu câu cho segmenter
    # Chỉ xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    # Tách từ (hỗ trợ tiếng Việt)
    try:
        words = word_tokenize(text, format="text").split()
        return words
    except:
        return text.split()

def tokenize_with_punctuation(text):
    # Tách từ nhưng giữ lại dấu câu . ! ? cho segmenter
    try:
        # Tách từ bằng underthesea
        words = word_tokenize(text, format="text").split()
        # Giữ lại các dấu câu như các token riêng biệt
        result = []
        for word in words:
            # Nếu từ kết thúc bằng dấu câu, tách ra
            if word and word[-1] in '.!?':
                result.append(word[:-1])  # Từ không có dấu câu
                result.append(word[-1])   # Dấu câu riêng
            else:
                result.append(word)
        return result
    except:
        # Fallback: tách đơn giản nhưng giữ dấu câu
        words = []
        current_word = ""
        for char in text:
            if char.isalnum() or char in 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ':
                current_word += char
            elif char in '.!?':
                if current_word:
                    words.append(current_word)
                    current_word = ""
                words.append(char)
            elif char.isspace():
                if current_word:
                    words.append(current_word)
                    current_word = ""
            else:
                if current_word:
                    words.append(current_word)
                    current_word = ""
        if current_word:
            words.append(current_word)
        return [w for w in words if w.strip()]

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

def reconstruct_sentence(words):
    # Hàm ghép lại câu sau khi xử lý
    if not words:
        return ""
    
    # Ghép các từ lại thành câu, thêm khoảng trắng giữa các từ
    sentence = " ".join(words)
    return sentence

_logger = None

def setup_logging(log_file="preprocess_log.txt"):
    # Thiết lập logging quá trình xử lý (chỉ setup một lần)
    global _logger
    if _logger is None:
        # Xóa các handler cũ nếu có
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ],
            force=True
        )
        _logger = logging.getLogger(__name__)
    return _logger

def preprocess(file_path, enable_logging=True):
    # Hàm chính: tiền xử lý văn bản
    logger = setup_logging() if enable_logging else None
    
    if logger:
        logger.info(f"Bắt đầu xử lý file: {file_path}")
    
    try:
        # Đọc file
        original_text = read_file(file_path)
        if logger:
            logger.info(f"Đã đọc file thành công. Độ dài: {len(original_text)} ký tự")
        
        # Text gốc với dấu câu cho segmenter
        text_with_punctuation = clean_text_for_segmenter(original_text)
        if logger:
            logger.info("Đã chuẩn hóa text với dấu câu cho segmenter")
        
        # Text đã làm sạch (bỏ dấu câu) cho các mục đích khác
        cleaned_text = clean_text(original_text)
        if logger:
            logger.info("Đã làm sạch text: lowercase, bỏ ký tự đặc biệt")
        
        # Danh sách từ có dấu câu cho segmenter
        words_with_punctuation = tokenize_with_punctuation(text_with_punctuation)
        if logger:
            logger.info(f"Đã tách từ với dấu câu: {len(words_with_punctuation)} từ")
        
        # Danh sách từ đã làm sạch
        words = tokenize(cleaned_text)
        original_words = words.copy()
        if logger:
            logger.info(f"Đã tách từ: {len(original_words)} từ gốc")
        
        words = remove_stopwords(words)
        if logger:
            logger.info(f"Đã loại bỏ stopwords: còn {len(words)} từ")
        
        words = normalize_english(words)
        if logger:
            logger.info(f"Đã chuẩn hóa từ tiếng Anh: còn {len(words)} từ")
        
        # Ghép lại câu sau khi xử lý
        reconstructed_sentence = reconstruct_sentence(words)
        if logger:
            logger.info("Đã ghép lại câu sau khi xử lý")
            logger.info(f"Thống kê: {len(original_words)} từ gốc -> {len(words)} từ đã clean")
            logger.info(f"Hoàn thành xử lý file: {file_path}")
        
        return {
            'original_text': original_text,  # Text gốc hoàn toàn
            'clean_text': text_with_punctuation,  # Text với dấu câu cho segmenter
            'original': original_words,  # Từ gốc (đã làm sạch một phần)
            'cleaned': words,  # Từ đã làm sạch hoàn toàn
            'words_with_punctuation': words_with_punctuation,  # Danh sách từ có dấu câu cho segmenter
            'reconstructed_sentence': reconstructed_sentence,  # Câu đã ghép lại sau khi xử lý
            'original_count': len(original_words),
            'cleaned_count': len(words),
            'words_with_punctuation_count': len(words_with_punctuation)
        }
    except Exception as e:
        if logger:
            logger.error(f"Lỗi khi xử lý file {file_path}: {str(e)}")
        raise

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

