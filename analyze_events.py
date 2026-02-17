import pandas as pd
from datetime import timedelta

# ===== 파일 로드 =====
metrics = pd.read_csv("logs/metrics.csv", parse_dates=["timestamp"])
events = pd.read_csv("logs/events.csv", parse_dates=["timestamp"])

print("총 이벤트 수:", len(events))

# ===== 각 이벤트 분석 =====
for idx, event in events.iterrows():

    event_time = event["timestamp"]

    before_start = event_time - timedelta(seconds=30)
    after_end = event_time + timedelta(seconds=30)

    before_data = metrics[(metrics["timestamp"] >= before_start) &
                          (metrics["timestamp"] < event_time)]

    after_data = metrics[(metrics["timestamp"] > event_time) &
                         (metrics["timestamp"] <= after_end)]
    
    print("\n=== 이벤트 시각:", event_time, "===")
    print("이벤트 CPU:", event["cpu_pct"])
    print("이벤트 Threshold:", event["threshold"])

    if len(before_data) > 0:
        print("이전 30초 평균 CPU:", round(before_data["cpu_pct"].mean(), 2))

    if len(after_data) > 0:
        print("이후 30초 평균 CPU:", round(after_data["cpu_pct"].mean(), 2))
    
    print("원인 후보:", event["top_processes"])