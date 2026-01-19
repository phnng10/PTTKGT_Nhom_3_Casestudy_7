from segmenter import segment_by_sentence
from preprocess_text import preprocess

    #So khớp toàn bộ đoạn 

def brute_force_segment_match(segments1, segments2, threshold=0.6):
    matches = []

    for i in range(len(segments1)):
        for j in range(len(segments2)):
            sim = sentence_similarity(segments1[i], segments2[j])
            if sim >= threshold:
                matches.append((i, j,sim))

    return matches

    #So khớp từng nhóm từ 

def brute_force_word_group(words1, words2, group_size=5):
    results = []

    for i in range(len(words1) - group_size + 1):
        group1 = words1[i:i + group_size]

        for j in range(len(words2) - group_size + 1):
            group2 = words2[j:j + group_size]

            if group1 == group2:
                results.append((i, j, group1))

    return results

#Tính % giống nhau
def calculate_similarity(total_segments, matched_segments):
    if total_segments == 0:
        return 0
    return matched_segments / total_segments * 100



if __name__ == "__main__":

    data1 = preprocess("text1.txt")
    data2 = preprocess("text2.txt")

    text1 = data1["clean_text"]
    text2 = data2["clean_text"]

    words1 = data1["cleaned"]
    words2 = data2["cleaned"]

    # chia đoạn theo câu
    segments1 = segment_by_sentence(text1, 3)
    segments2 = segment_by_sentence(text2, 3)

    # so khớp đoạn
    matches = brute_force_segment_match(segments1, segments2)

    # tổng số đoạn của cả 2 văn bản
    total_segments = len(segments1) + len(segments2)

    #tính độ tương đồng cho cả text 1 và text 2
    similarity = calculate_similarity(total_segments, len(matches))*100

    print("Số đoạn văn bản 1:", len(segments1))
    print("Số đoạn văn bản 2:",len(segments2))
    print("Số đoạn trùng:", len(matches))
    print("Phần trăm giống nhau:", similarity, "%")

    print("\nCác đoạn trùng nhau:")
    for i, j in matches:
        print(f"Đoạn {i} (Text1) trùng với đoạn {j} (Text2)")

    # so khớp nhóm từ
    word_matches = brute_force_word_group(words1, words2, 5)

    print("\nSố nhóm từ trùng:", len(word_matches))
    print("\n Các nhóm từ trùng nhau:")
    for i,j, group in word_matches:

        print(f"-Nhóm từ tại vị trí {i} (Text 1) trùng với vị trí {j} (Text 2)")

        print(" Nội dung nhóm từ:","".join(group))
