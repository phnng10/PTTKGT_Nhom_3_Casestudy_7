import re

def split_into_sentences(text):
    #chia văn bản thành câu dựa trên dấu câu
    if not text or not text.strip():
        return []

    #tách câu theo . ! ?
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

 #chia văn bản thành các đoạn, mỗi đoạn gồm N câu
def segment_by_sentence(text, sentences_per_segment=3):
    sentences = split_into_sentences(text)
    if len(sentences) < sentences_per_segment:
        return []

    segments = []
    for i in range(0, len(sentences), sentences_per_segment):
        segment = " ".join(sentences[i:i + sentences_per_segment])
        if segment:
            segments.append(segment)

    return segments

#chia theo số lượng từ
def segment_by_length(words, segment_length=50):
    if not words or len(words) < segment_length:
        return []

    segments = []
    for i in range(0, len(words), segment_length):
        chunk = words[i:i + segment_length]
        if len(chunk) >= segment_length // 2:
            segments.append(chunk)

    return segments

#kiểm tra đầu vào trước khi chia đoạn
def validate_input(text, words):
    errors = []
    if not text or not text.strip():
        errors.append("Văn bản rỗng")
    if not words or len(words) < 10:
        errors.append("Danh sách từ quá ngắn")
    return errors


if __name__ == "__main__":
    from preprocess_text import preprocess

    data = preprocess("text1.txt")
    text = data["clean_text"]
    words = data["cleaned"]

    errors = validate_input(text, words)
    if errors:
        print("Lỗi input:")
        for e in errors:
            print("-", e)
        exit()

    print("Chia theo câu:")
    seg_sent = segment_by_sentence(text, 3)
    print("Số đoạn:", len(seg_sent))

    print("\nChia theo độ dài:")
    seg_len = segment_by_length(words, 50)
    print("Số đoạn:", len(seg_len))
