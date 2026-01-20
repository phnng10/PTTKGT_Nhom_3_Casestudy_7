import os
import matplotlib.pyplot as plt
from datetime import datetime

# Tên hiển thị rút gọn cho các chiến lược
# Dùng để hiển thị trên biểu đồ cho gọn và dễ đọc
DISPLAY_NAME = {
    "Jaccard Similarity": "Jaccard",
    "Cosine Similarity (Segment-based)": "Cosine",
    "Brute Force Matching": "Bruteforce",
    "Edit Distance (Levenshtein DP)": "Edit Distance",
    "Divide and Conquer (Pruning & Weighted)": "Divide & Conquer"
}

# Màu pastel tương ứng cho từng chiến lược
# Giúp biểu đồ dễ nhìn và phân biệt rõ các phương pháp
PASTEL_COLORS = {
    "Jaccard": "#A8D5BA",           
    "Cosine": "#A7C7E7",            
    "Bruteforce": "#D7BDE2",       
    "Edit Distance": "#F9E79F",     
    "Divide & Conquer": "#F5B7B1"   
}

def plot_bar(data, title, ylabel, filename, log_scale=False):
    """
    Vẽ biểu đồ cột cho một chỉ số thống kê
    data: dict {strategy_name: value}
    title: tiêu đề biểu đồ
    ylabel: nhãn trục Y
    filename: tên file ảnh đầu ra
    log_scale: có sử dụng thang log cho trục Y hay không
    """
    names = []
    values = []
    colors = []

    # Duyệt từng chiến lược để lấy tên hiển thị, giá trị và màu sắc
    for k, v in data.items():
        short = DISPLAY_NAME.get(k, k)
        names.append(short)
        values.append(v)
        colors.append(PASTEL_COLORS.get(short, "#CCCCCC"))

    # Khởi tạo biểu đồ
    plt.figure(figsize=(7, 4))
    plt.bar(names, values, color=colors)

    # Thiết lập tiêu đề và nhãn
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=0, fontsize=10)

    # Nếu cần, dùng thang log cho trục Y (phù hợp khi so sánh thời gian)
    if log_scale:
        plt.yscale("log")

    # Thêm lưới để dễ quan sát
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    # Lưu biểu đồ ra file
    plt.savefig(filename)
    plt.close()

def build_table(results):
    """
    Tạo bảng HTML hiển thị kết quả của từng chiến lược
    results: danh sách kết quả của một bộ kiểm thử
    """
    html = """
    <table>
      <tr>
        <th>Chiến lược</th>
        <th>Độ giống</th>
        <th>Thời gian (s)</th>
      </tr>
    """

    # Thêm từng dòng dữ liệu vào bảng
    for r in results:
        strategy = r.get("strategy", "N/A")
        sim = r.get("similarity_score", 0)
        time = r.get("time_seconds", 0)

        html += f"""
        <tr>
          <td>{strategy}</td>
          <td>{round(sim, 4)}</td>
          <td>{round(time, 6)}</td>
        </tr>
        """

    html += "</table>"
    return html

def build_report(all_cases, output_file="report.html"):
    """
    Xây dựng báo cáo HTML tổng hợp cho tất cả các bộ kiểm thử
    all_cases: danh sách các bộ test và kết quả tương ứng
    """

    avg_similarity = {}
    avg_time = {}
    count = {}

    # Tính tổng độ giống và thời gian cho từng chiến lược
    for case in all_cases:
        for r in case.get("results", []):
            name = r.get("strategy")
            if not name:
                continue

            avg_similarity[name] = avg_similarity.get(name, 0) + r.get("similarity_score", 0)
            avg_time[name] = avg_time.get(name, 0) + r.get("time_seconds", 0)
            count[name] = count.get(name, 0) + 1

    # Tính giá trị trung bình
    for k in avg_similarity:
        avg_similarity[k] /= count[k]
        avg_time[k] /= count[k]

    # Tạo thư mục lưu biểu đồ nếu chưa tồn tại
    os.makedirs("charts", exist_ok=True)

    # Vẽ biểu đồ độ giống trung bình
    plot_bar(
        avg_similarity,
        title="Độ giống trung bình giữa các chiến lược",
        ylabel="Similarity",
        filename="charts/similarity.png"
    )

    # Vẽ biểu đồ thời gian chạy trung bình (dùng thang log)
    plot_bar(
        avg_time,
        title="Thời gian chạy trung bình",
        ylabel="Time (seconds, log scale)",
        filename="charts/time.png",
        log_scale=True
    )

    # Nội dung HTML của báo cáo
    html = f"""
    <html>
    <head>
      <meta charset="utf-8">
      <title>Báo cáo so sánh chiến lược</title>
      <style>
        body {{ font-family: Arial; margin: 30px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 70%; margin-bottom: 25px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
        th {{ background: #f2f2f2; }}
        img {{ width: 420px; margin: 15px 0; }}
        .case {{ margin-bottom: 40px; }}
      </style>
    </head>
    <body>
      <h1>BÁO CÁO KẾT QUẢ SO SÁNH</h1>
      <p>Thời gian tạo: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>

      <h2>Biểu đồ tổng quan</h2>
      <img src="charts/similarity.png">
      <img src="charts/time.png">

      <h2>Chi tiết từng bộ kiểm thử</h2>
    """

    # Thêm kết quả chi tiết cho từng bộ test
    for case in all_cases:
        html += f"""
        <div class="case">
          <h3>{case.get("case", "")}</h3>
          {build_table(case.get("results", []))}
        </div>
        """

    html += "</body></html>"

    # Ghi báo cáo ra file HTML
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Đã tạo báo cáo: {output_file}")

def generate_html_report(all_cases, output_file="report.html"):
    """
    Hàm wrapper để gọi xây dựng báo cáo
    Dùng cho module main import và sử dụng
    """
    build_report(all_cases, output_file)
