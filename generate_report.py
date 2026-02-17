import os
from datetime import timedelta, datetime

import pandas as pd

METRICS_PATH = "logs/metrics.csv"
EVENTS_PATH = "logs/events.csv"
OUT_DIR = "reports"

WINDOW_SEC = 30  # 이벤트 전후 몇 초를 비교할지

def safe_mean(series):
    """비어 있으면 None, 아니면 평균(float)."""
    if series is None or len(series)  == 0:
        return None
    return float(series.mean())

def fmt(x, digits=2):
    """None이면 '-', 숫자면 소수점 포맷."""
    if x is None:
        return "-"
    return f"{x:.{digits}f}"

def main():
    # 1) 입력 파일 존재 확인
    if not os.path.exists(METRICS_PATH):
        raise FileNotFoundError(f"metrics 파일이 없습니다: {METRICS_PATH}")
    if not os.path.exists(EVENTS_PATH):
        raise FileNotFoundError(f"events 파일이 없습니다: {EVENTS_PATH}")

    # 2) CSV 로드 (timestamp를 datetime으로 파싱)
    metrics = pd.read_csv(METRICS_PATH, parse_dates=["timestamp"])
    events = pd.read_csv(EVENTS_PATH, parse_dates=["timestamp"])

    # 3) 기본 상태 출력(디버그/확인용)
    print("[load] metrics rows:", len(metrics))
    print("[load] events rows:", len(events))
    print("[load] metrics range:", metrics["timestamp"].min(), "~", metrics["timestamp"].max())

    # 3) 출력 폴더 준비
    os.makedirs(OUT_DIR, exist_ok=True)

    # 4) 리포트 파일명(고정)
    out_path = os.path.join(OUT_DIR, "pc_rca_report.md")

    # 5) 리포트 작성
    lines = []
    lines.append("# PC RCA 자동 리포트")
    lines.append("")
    lines.append(f"- metrics rows: {len(metrics)}")
    lines.append(f"- events rows: {len(events)}")
    lines.append(f"- metrics time range: {metrics['timestamp'].min()} ~ {metrics['timestamp'].max()}")
    lines.append(f"- window: ±{WINDOW_SEC}s")
    lines.append("")

    if len(events) == 0:
        lines.append("이벤트가 없습니다. (CPU_ANOMALY 미발생)")
    else:
        lines.append("## 이벤트 요약")
        lines.append("")
        # Markdown 표 헤더
        lines.append("| # | timestamp | cpu | ewma | threshold | cpu_before(30s avg) | cpu_after(30s avg) | top_processes |")
        lines.append("|---:|---|---:|---:|---:|---:|---:|---|")

        for i, ev in events.iterrows():
            t = ev["timestamp"]
            before_start = t - timedelta(seconds=WINDOW_SEC)
            after_end = t + timedelta(seconds=WINDOW_SEC)

            before = metrics[(metrics["timestamp"] >= before_start) & (metrics["timestamp"] < t)]
            after = metrics[(metrics["timestamp"] > t) & (metrics["timestamp"] < after_end)]

            cpu_before = safe_mean(before["cpu_pct"]) if len(before) else None
            cpu_after = safe_mean(after["cpu_pct"]) if len(after) else None

            lines.append(
                f"| {i+1} | {t} | {fmt(ev['cpu_pct'])} | {fmt(ev['cpu_ewma'])} | {fmt(ev['threshold'])} | "
                f"{fmt(cpu_before)} | {fmt(cpu_after)} | {ev['top_processes']} |"
            )
        
        lines.append("")
        lines.append("## 해석 가이드")
        lines.append("")
        lines.append("- **cpu_before**가 낮고 이벤트 순간 **cpu**가 높으면: 순간적인 부하 스파이크 가능성이 큼")
        lines.append("- **top_processes**에 `python(...) cpu=99.x` 같은 값이 보이면: 해당 PID 프로세스가 주 원인 후보")
        lines.append("- threshold는 `ewma + K * dev` 기반이라, 평소 변동이 크면 threshold도 같이 커짐")

        # 6) 파일 저장
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print("[report] saved:", out_path)

if __name__ == "__main__":
    main()