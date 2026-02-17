"""
PC 성능 저하 감지 + 원인(RCA) 식별기
- 주기적으로 시스템 지표 + Top 프로세스를 수집
- STEP 1: 2초마다 CPU/MEM을 계속 출력(수집기 최소 버전)
- STEP 2: CPU/MEM을 2초마다 수집하고 metrics.csv에 저장
- STEP 3: CPU EWMA(지수이동평균) 기반 이상 감지 + 이벤트 로그(events.csv)
"""

import time
import psutil
import csv
import os

# ===== 사용자 설정 =====
INTERVAL_SEC = 2.0

LOG_DIR = 'logs'
METRICS_PATH = os.path.join(LOG_DIR, "metrics.csv")
EVENTS_PATH = os.path.join(LOG_DIR, "events.csv")

TOP_N = 3   # 출력할 Top 프로세스 개수

# EWMA 설정
ALPHA = 0.2         # EWMA 반영 비율(0~1): 클수록 "최근 값"에 민감
WARMUP_N = 10       # EWMA가 안정화되기 전까지는 감지 안 함(측정 횟수)
K = 3.0             # 이상 기준 배수(클수록 덜 민감)
EPS = 1e-6          # 0 나누기 방지 

def ensure_log_file():
    """logs 폴더/CSV 헤더 생성(없을 때만)."""
    os.makedirs(LOG_DIR, exist_ok=True)

    if not os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, 'w', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "cpu_pct", "mem_pct"])
    
    if not os.path.exists(EVENTS_PATH):
        with open(EVENTS_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "event_type",
                "cpu_pct", "cpu_ewma", "cpu_dev_ewma", "threshold",
                "top_processes"
            ])

def get_top_processes(top_n=3):
    """CPU 사용률이 높은 프로세스 TopN을 스냅샷으로 가져오기."""
    processes = []

    for p in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_info"]):
        try:
            info = p.info
            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu": info["cpu_percent"],
                "mem_mb": info["memory_info"].rss / (1024*1024) if info.get("memory_info") else 0.0
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    processes.sort(key=lambda x: x["cpu"], reverse=True)

    return processes[:top_n]

def ewma_update(prev: float, x: float, alpha: float) -> float:
    """EWMA 업데이트: new = alpha*x + (1-alpha)*prev"""
    return alpha * x + (1.0 - alpha) * prev

def main():
    print(f"[pc_rca_monitor] start | interval={INTERVAL_SEC}s (Ctrl+C to stop)")
    ensure_log_file()

    # (중요) cpu_percent는 '이전 호출 이후 변화' 기반이라 워밍업 호출 
    psutil.cpu_percent(interval=None)
    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except Exception:
            pass
    
    # EWMA 상태값: 평균(ewma), 절대편차(ewma_dev)
    cpu_ewma = None
    cpu_dev_ewma = 0.0
    n = 0
    
    try:
        while True:
            
            # ----- 1. 프로세스 CPU 워밍업 -----
            for p in psutil.process_iter():
                try:
                    p.cpu_percent(interval=None)
                except:
                    pass
            # ----- 2. 동일 구간 확보 -----
            time.sleep(INTERVAL_SEC)   
                        
            # ----- 3. 동일 시간 기준 측정 -----
            cpu = float(psutil.cpu_percent(interval=None))
            mem = float(psutil.virtual_memory().percent)
            ts = time.strftime("%Y-%m-%d %H:%M:%S")

            # ===== metrics.csv 기록 =====  
            with open(METRICS_PATH, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([ts, cpu, mem])
        
            # ===== EWMA 업데이트 =====
            if cpu_ewma is None:
                cpu_ewma = cpu  # 첫 값으로 초기화
            else:
                cpu_ewma = ewma_update(cpu_ewma, cpu, ALPHA)
        
            # 절대 편차의 EWMA(가벼운 변동성 추정)
            dev = abs(cpu - cpu_ewma)
            cpu_dev_ewma = ewma_update(cpu_dev_ewma, dev, ALPHA)

            n += 1

            # ===== 이상 감지 =====
            # 임계값 = 평균 + K * (평균 절대편차)
            threshold = cpu_ewma + K * max(cpu_dev_ewma, EPS)
            is_ready = (n >= WARMUP_N)
            is_anomaly = is_ready and (cpu > threshold)

            # ===== 출력 =====
            print("CPU:", cpu, "% | MEM:", mem, "% | EWMA:", round(cpu_ewma, 2), "| TH:", round(threshold, 2))

            # 원인 후보(Top 프로세스)
            top = get_top_processes(TOP_N)
            for proc in top:
                print(" ->", proc["name"], "| CPU:", proc["cpu"], "%")
            
            # ===== 이벤트 기록 =====
            if is_anomaly:
                # Top 프로세스 정보를 한 줄 문자열로 저장(나중에 분석용)
                top_str = "; ".join([f'{p["name"]}({p["pid"]}) cpu={p["cpu"]:.1f}' for p in top])

                print("!!! ALERT: CPU anomaly detected !!!")

                with open(EVENTS_PATH, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        ts, "CPU_ANOMALY",
                        cpu, round(cpu_ewma, 4), round(cpu_dev_ewma, 4), round(threshold, 4),
                        top_str
                    ])
            
            time.sleep(INTERVAL_SEC)

    except KeyboardInterrupt:
        print("\n[pc_rca_monitor] stopped")

if __name__ == "__main__":
    main()