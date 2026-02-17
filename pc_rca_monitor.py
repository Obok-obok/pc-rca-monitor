"""
PC 성능 저하 감지 + 원인(RCA) 식별기 (Z-score 버전)
- INTERVAL_SEC 주기로 CPU/MEM 수집 → logs/metrics.csv
- EWMA 평균 + EWMA 분산(=표준편차)로 Z-score 계산
- z_score > Z_THRESHOLD 이면 이상 이벤트 기록 → logs/events.csv
- 이상 시점의 Top 프로세스(원인 후보)도 함께 저장

실행:
  python pc_rca_monitor.py
중지:
  Ctrl + C
"""

import time
import psutil
import csv
import os

# ===== 사용자 설정 =====
INTERVAL_SEC = 2.0

LOG_DIR = "logs"
METRICS_PATH = os.path.join(LOG_DIR, "metrics.csv")
EVENTS_PATH = os.path.join(LOG_DIR, "events.csv")

TOP_N = 3

# Z-score 설정
ALPHA = 0.2          # EWMA 반영 비율
WARMUP_N = 10        # 워밍업 횟수(이전엔 감지 안 함)
Z_THRESHOLD = 2.0    # z-score 임계값
EPS = 1e-6           # 0 나누기 방지


def ensure_log_files():
    """logs 폴더/CSV 헤더 생성(없을 때만)."""
    os.makedirs(LOG_DIR, exist_ok=True)

    if not os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "cpu_pct", "mem_pct"])

    if not os.path.exists(EVENTS_PATH):
        with open(EVENTS_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "timestamp", "event_type",
                "cpu_pct", "cpu_ewma", "cpu_std",
                "z_score", "z_threshold",
                "top_processes"
            ])


def ewma_update(prev: float, x: float, alpha: float) -> float:
    """EWMA 업데이트: new = alpha*x + (1-alpha)*prev"""
    return alpha * x + (1.0 - alpha) * prev


def get_top_processes(top_n=3):
    """CPU 사용률이 높은 프로세스 TopN 스냅샷."""
    processes = []
    for p in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_info"]):
        try:
            info = p.info
            processes.append({
                "pid": info["pid"],
                "name": info.get("name") or "unknown",
                "cpu": float(info.get("cpu_percent") or 0.0),
                "mem_mb": (info["memory_info"].rss / (1024 * 1024)) if info.get("memory_info") else 0.0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda x: x["cpu"], reverse=True)
    return processes[:top_n]


def main():
    print(f"[pc_rca_monitor] start | interval={INTERVAL_SEC}s | z_th={Z_THRESHOLD} (Ctrl+C to stop)")
    ensure_log_files()

    # (중요) cpu_percent는 "이전 호출 이후" 기반이라 워밍업
    psutil.cpu_percent(interval=None)
    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except Exception:
            pass

    cpu_ewma = None
    cpu_var_ewma = 0.0  # 분산(EWMA)
    n = 0

    try:
        while True:
            # ----- 1) 프로세스 CPU 측정 기준점 잡기 (동기화 개선) -----
            for p in psutil.process_iter():
                try:
                    p.cpu_percent(interval=None)
                except Exception:
                    pass

            # ----- 2) 동일 구간 확보 -----
            time.sleep(INTERVAL_SEC)

            # ----- 3) 동일 시간 구간 기준 측정 -----
            cpu = float(psutil.cpu_percent(interval=None))
            mem = float(psutil.virtual_memory().percent)
            ts = time.strftime("%Y-%m-%d %H:%M:%S")

            # ----- metrics.csv 기록 -----
            with open(METRICS_PATH, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([ts, cpu, mem])

            # ----- EWMA 평균/분산 업데이트 -----
            if cpu_ewma is None:
                cpu_ewma = cpu
            else:
                cpu_ewma = ewma_update(cpu_ewma, cpu, ALPHA)

            diff = cpu - cpu_ewma
            cpu_var_ewma = ewma_update(cpu_var_ewma, diff * diff, ALPHA)
            cpu_std = (cpu_var_ewma + EPS) ** 0.5

            z_score = (cpu - cpu_ewma) / cpu_std

            n += 1
            is_ready = (n >= WARMUP_N)
            is_anomaly = is_ready and (z_score > Z_THRESHOLD)

            # ----- 출력(Z-score 중심으로 정리) -----
            print(
                "CPU:", cpu, "% | MEM:", mem, "% | EWMA:", round(cpu_ewma, 2),
                "| STD:", round(cpu_std, 2), "| Z:", round(z_score, 2)
            )

            top = get_top_processes(TOP_N)
            for proc in top:
                print("  ->", proc["name"], "| CPU:", proc["cpu"], "%")

            # ----- 이벤트 기록 -----
            if is_anomaly:
                top_str = "; ".join([f'{p["name"]}({p["pid"]}) cpu={p["cpu"]:.1f}' for p in top])
                print("!!! ALERT: CPU anomaly detected (Z-score) !!!")

                with open(EVENTS_PATH, "a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow([
                        ts, "CPU_ANOMALY_Z",
                        round(cpu, 4), round(cpu_ewma, 4), round(cpu_std, 4),
                        round(z_score, 4), Z_THRESHOLD,
                        top_str
                    ])

    except KeyboardInterrupt:
        print("\n[pc_rca_monitor] stopped")


if __name__ == "__main__":
    main()