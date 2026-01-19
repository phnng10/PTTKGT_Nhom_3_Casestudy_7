"""Phân tích kết quả từ các chiến lược"""
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

RESULTS_DIR = "evaluation_results"

#Đọc tất cả file JSON trong thư mục results
def load_all_results():
    all_data = []
    if not os.path.exists(RESULTS_DIR):
        print(f"Không tìm thấy thư mục {RESULTS_DIR}")
        return []
    for fname in os.listdir(RESULTS_DIR):
        if fname.endswith('json'):
            fpath = os.path.join(RESULTS_DIR, fname)
            with open(fpath, 'r', encoding = 'utf-8') as f:
                data = json.load(f)
                all_data.append(data)
    return all_data

#Tính thống kê cơ bản: trung bình, min, max
def calc_stats(results):
    stats = defaultdict(lambda: {'scores': [], 'times': []})
    for case in results:
        for r in case.get('results', []):
            strategy = r['strategy']
            stats[strategy]['scores'].append(r['similarity_score'])
            stats[strategy]['times'].append(r['time_seconds'])
    
    #Tính mean, std
    summary = {}
    for strat, vals in stats.items():
        scores = vals['scores']
        times = vals['times']
        summary[strat] = {
            'avg_score': np.mean(scores) if scores else 0,
            'std_score': np.std(scores) if scores else 0,
            'min_score': np.min(scores) if scores else 0,
            'max_score': np.max(scores) if scores else 0,
            'avg_time': np.mean(times) if times else 0,
            'total_runs': len(scores)
        }
    return summary

#Vẽ biểu đồ so sánh 3 chiến lược: Vét cạn, Quy hoạch động, Chia để trị
def plot_comparison(stats):
    strategies = list(stats.keys())
    avg_scores = [stats[s]['avg_score'] for s in strategies]
    avg_times = [stats[s]['avg_time'] for s in strategies]
    std_scores = [stats[s]['std_score'] for s in strategies]
    fig, axes = plt.subplots(1, 3, figsize=(15,6))
    
    #Biểu đồ 1: Độ chính xác trung bình
    axes[0].bar(strategies, avg_scores)
    axes[0].set_ylabel('Similarity Score')
    axes[0].set_title('Độ chính xác trung bình')
    axes[0].set_ylim([0, 1])
    
    #Biểu đồ 2: Tốc độ (thời gian)
    axes[1].bar(strategies, avg_times)
    axes[1].set_ylabel('Time (seconds)')
    axes[1].set_title('Thời gian chạy trung bình')
    
    #Biểu đồ 3: Độ ổn định (std)
    axes[2].bar(strategies, std_scores)
    axes[2].set_ylabel('Std Dev')
    axes[2].set_title('Độ ổn định (std thấp = tốt)')
    
    plt.tight_layout()
    plt.savefig('comparison_chart.png', dpi=150)
    print("Đã lưu biểu đồ: comparison_chart.png")

#Xuất báo cáo file text
def export_report(stats):
    with open('analysis_report.txt', 'w', encoding = 'utf-8') as f:
        f.write("=== BÁO CÁO PHÂN TÍCH KẾT QUẢ ===\n\n")

        for strat, data in stats.items():
            f.write(f"\n---{strat} ---\n")
            f.write(f"Độ chính xác TB: {data['avg_score']:.4f}\n")
            f.write(f"Độ lệch chuẩn: {data['std_score']:.4f}\n")
            f.write(f"Min/Max: {data['min_score']:.4f} / {data['max_score']:.4f}\n")
            f.write(f"Thời gian TB: {data['avg_time']:.4f}s\n")
            f.write(f"Số lần chạy: {data['total_runs']}\n")
    print("Đã xuất báo cáo: analysis_report.txt")

if __name__ == "__main__":
    print("Đang phân tích kết quả ...")

    results = load_all_results()
    if not results:
        print("Không có dữ liệu")
        exit()

    stats = calc_stats(results)

    print("\n=== THỐNG KÊ ===")
    for s, d in stats.items():
        print(f"{s}: Score={d['avg_score']:.3f}, Time={d['avg_time']:.3f}s")

    plot_comparison(stats)
    export_report(stats)
