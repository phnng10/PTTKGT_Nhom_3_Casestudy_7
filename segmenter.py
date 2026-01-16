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

#kiểm tra đầu vào trước và sau khi chia đoạn
def validate_input(text, words, segments=None, min_words=10):
    errors = []
    
    #trước
    if not text or not text.strip():
        errors.append("Văn bản rỗng")
    if not words or len(words) < min_words:
        errors.append("Danh sách từ quá ngắn")
     
    #sau
    if segments is not None:
        if not segments:
            errors.append("không có đoạn nào sau khi chia.")
        #đoạn rỗng
        empty_segments = [i for i, seg in enumerate(segments) if not seg]
        if empty_segments:
            errors.append(f"Có đoạn rỗng tại: {empty_segments}")
        #đoạn quá ngắn
        short_segments = [i for i, seg in enumerate(segments) if len(seg) < min_words]
        if short_segments:
            errors.append(f"Có {len(short_segments)} đoạn quá ngắn (< {min_words} từ đoạn): {short_segments}")
        #kiểm tra câu dính và câu dài bất thường
        lengths = [len(seg) for seg in segments if seg]
        if lengths:
            max_len = max(lengths)
            min_len_seg = min(lengths)
            
            if min_len_seg > 0 and max_len > 3 * min_len_seg:
                errors.append("Độ dài các đoạn chênh lệch lớn(tối đa>3 lần tối thiểu) – có thể dính câu")
    return errors
   
if __name__ == "__main__":
    from preprocess_text import preprocess

    data1 = preprocess("text1.txt")
    data2 = preprocess("text2.txt")

    text1 = data1["clean_text"]
    text2 = data2["clean_text"]

    words1 = data1["cleaned"]
    words2 = data2["cleaned"]

    words1_punct = data1["words_with_punctuation"]
    words2_punct = data2["words_with_punctuation"]

    errors1 = validate_input(text1, words1)
    errors2 = validate_input(text2, words2)

    if errors1 or errors2:
        print("Lỗi input:")

        if errors1:
            print("Text1:")
            for e in errors1:
                print(" -", e)

        if errors2:
            print("Text2:")
            for e in errors2:
                print(" -", e)
        exit()
    print("Text 1: ")
    print("Chia theo câu:")
    seg_sent = segment_by_sentence(text1, 3)
    print("Số đoạn:", len(seg_sent))

    print("\nChia theo độ dài:")
    seg_len = segment_by_length(words1, 50)
    print("Số đoạn:", len(seg_len))
    
    print("Text 2: ")
    print("Chia theo câu:")
    seg_sent = segment_by_sentence(text2, 3)
    print("Số đoạn:", len(seg_sent))

    print("\nChia theo độ dài:")
    seg_len = segment_by_length(words2, 50)
    print("Số đoạn:", len(seg_len))
