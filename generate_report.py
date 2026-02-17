import os
from datetime import timedelta

import pandas as pd

METRICS_PATH = "logs/metrics.csv"
EVENTS_PATH = "logs/events.csv"
OUT_DIR = "reports"

WINDOW_SEC = 30  # 이벤트 전후 비교 범위(초)

def safe_mean(series):
    if series is None or len(series) == 0:
        return None
    return float(series.mean())

def fmt(x, digits=2):
    if x is None:
        return "-"
    return f"{x:.{digits}f}"

def main():
    if not os.path.exists(METRICS_PATH):
        raise FileNotFoundError(f"metrics 파일이 없습니다: {METRICS_PATH}")
    if not os.path.exists(EVENTS_PATH):
        raise FileNotFoundError(f"events 파일이 없습니다: {EVENTS_PATH}")

    metrics = pd.read_csv(METRICS_PATH, parse_dates=["timestamp"])
    events = pd.read_csv(EVENTS_PATH, parse_dates=["timestamp"])

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "pc_rca_report.md")

    lines = []
    lines.append("# PC RCA 자동 리포트 (Z-score)")
    lines.append("")
    lines.append(f"- metrics rows: {len(metrics)}")
    lines.append(f"- events rows: {len(events)}")
    lines.append(f"- metrics time range: {metrics['timestamp'].min()} ~ {metrics['timestamp'].max()}")
    lines.append(f"- window: ±{WINDOW_SEC}s")
    lines.append("")

    if len(events) == 0:
        lines.append("이벤트가 없습니다. (CPU_ANOMALY_Z 미발생)")
    else:
        lines.append("## 이벤트 요약")
        lines.append("")
        lines.append("| # | timestamp | cpu | ewma | std | z | z_th | cpu_before(30s avg) | cpu_after(30s avg) | top_processes |")
        lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---|")

        for i, ev in events.iterrows():
            t = ev["timestamp"]
            before_start = t - timedelta(seconds=WINDOW_SEC)
            after_end = t + timedelta(seconds=WINDOW_SEC)

            before = metrics[(metrics["timestamp"] >= before_start) & (metrics["timestamp"] < t)]
            after  = metrics[(metrics["timestamp"] > t) & (metrics["timestamp"] <= after_end)]

            cpu_before = safe_mean(before["cpu_pct"]) if len(before) else None
            cpu_after  = safe_mean(after["cpu_pct"]) if len(after) else None

            # 컬럼이 없을 수도 있으니 get으로 안전 처리
            cpu_std = ev.get("cpu_std", None)
            z_score = ev.get("z_score", None)
            z_th = ev.get("z_threshold", None)

            lines.append(
                f"| {i+1} | {t} | {fmt(ev.get('cpu_pct'))} | {fmt(ev.get('cpu_ewma'))} | {fmt(cpu_std)} | "
                f"{fmt(z_score)} | {fmt(z_th)} | {fmt(cpu_before)} | {fmt(cpu_after)} | {ev.get('top_processes','')} |"
            )

        lines.append("")
        lines.append("## 해석 가이드")
        lines.append("")
        lines.append("- **z**가 **z_th**를 넘으면: 평소 대비 통계적으로 드문 CPU 상승(이상)으로 판단")
        lines.append("- **cpu_before**가 낮고 이벤트 순간 **cpu**가 높으면: 스파이크/이상 발생 시점으로 해석")
        lines.append("- **cpu_after**가 높게 유지되면: 단발성 스파이크가 아닌 지속 부하 가능성")
        lines.append("- **top_processes**에서 높은 CPU를 점유한 PID가 Root Cause 후보")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("[report] saved:", out_path)

if __name__ == "__main__":
    main()
