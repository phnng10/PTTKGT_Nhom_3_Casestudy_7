# report_builder.py
# Nhiệm vụ: Tạo file report.html từ dữ liệu kết quả
# - Có tiêu đề, mô tả
# - Bảng so sánh 3 chiến lược
# - 1–2 biểu đồ bằng matplotlib
# - CSS nhẹ nhàng cho dễ nhìn

import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

# =========================
# VẼ BIỂU ĐỒ
# =========================

def plot_bar(data, title, filename):
    """Vẽ biểu đồ cột đơn giản từ dict {strategy: value}"""
    names = list(data.keys())
    values = list(data.values())

    #Màu theo chiến lược
    color_map = {
        "Jaccard Similarity": "#4CAF50",                 
        "Cosine Similarity (Segment-based)": "#2196F3",  
        "Edit Distance (Levenshtein DP)": "#FF9800",     
        "Divide and Conquer (Pruning & Weighted)": "#F44336",
        "Brute Force Matching": "#AB71B5"  
    }

    colors = [color_map.get(name, "#9E9E9E") for name in names]  

    plt.figure(figsize=(8, 5))
    plt.bar(names, values, color=colors)
    plt.title(title)
    plt.ylabel(title)
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.5)  # nhìn xịn hơn
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# =========================
# TẠO BẢNG HTML
# =========================

def build_table(results):
    """Tạo bảng HTML từ list kết quả chuẩn format"""
    html = """
    <table>
      <tr>
        <th>Chiến lược</th>
        <th>Similarity</th>
        <th>Thời gian (s)</th>
      </tr>
    """
    for r in results:
        html += f"""
        <tr>
          <td>{r['strategy']}</td>
          <td>{round(r['similarity_score'], 4)}</td>
          <td>{round(r['time_seconds'], 6)}</td>
        </tr>
        """
    html += "</table>"
    return html

# =========================
# GHI FILE HTML
# =========================

def build_report(all_cases, output_file="report.html"):
    """Nhận list các case test và xuất ra report.html"""

    # Lấy dữ liệu trung bình theo chiến lược
    avg_similarity = {}
    avg_time = {}
    count = {}

    for case in all_cases:
        for r in case["results"]:
            name = r["strategy"]
            avg_similarity[name] = avg_similarity.get(name, 0) + r["similarity_score"]
            avg_time[name] = avg_time.get(name, 0) + r["time_seconds"]
            count[name] = count.get(name, 0) + 1

    for k in avg_similarity:
        avg_similarity[k] /= count[k]
        avg_time[k] /= count[k]

    # Vẽ biểu đồ
    os.makedirs("charts", exist_ok=True)
    plot_bar(avg_similarity, "Độ giống trung bình", "charts/similarity.png")
    plot_bar(avg_time, "Thời gian chạy trung bình", "charts/time.png")

    # HTML cơ bản
    html = f"""
    <html>
    <head>
      <meta charset='utf-8'>
      <title>Báo cáo so sánh chiến lược</title>
      <style>
        body {{ font-family: Arial; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 60%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
        th {{ background: #f2f2f2; }}
        img {{ width: 400px; margin: 10px 0; }}
        .case {{ margin-bottom: 30px; }}
      </style>
    </head>
    <body>
      <h1>BÁO CÁO KẾT QUẢ SO SÁNH</h1>
      <p>Thời gian tạo: {datetime.now()}</p>

      <h2>Biểu đồ tổng quan</h2>
      <img src='charts/similarity.png'>
      <img src='charts/time.png'>

      <h2>Chi tiết từng bộ test</h2>
    """

    for case in all_cases:
        html += f"""
        <div class='case'>
          <h3>{case['case']}</h3>
          {build_table(case['results'])}
        </div>
        """

    html += "</body></html>"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Đã tạo báo cáo: {output_file}")

def generate_html_report(all_cases, output_file="report.html"):
    build_report(all_cases, output_file)