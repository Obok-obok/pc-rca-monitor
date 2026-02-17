import os
from datetime import timedelta

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

METRICS_PATH = "logs/metrics.csv"
EVENTS_PATH = "logs/events.csv"

WINDOW_SEC = 60  # 이벤트 전후 표시 범위(초)

st.set_page_config(page_title="PC RCA Dashboard", layout="wide")
st.title("PC RCA Dashboard")
st.caption("CPU anomaly detection + root cause candidates (Top processes)")

def load_csv():
    metrics = None
    events = None

    if os.path.exists(METRICS_PATH):
        metrics = pd.read_csv(METRICS_PATH, parse_dates=["timestamp"])
    if os.path.exists(EVENTS_PATH):
        events = pd.read_csv(EVENTS_PATH, parse_dates=["timestamp"])
    return metrics, events

metrics, events = load_csv()

# ===== 사이드바: 상태 =====
with st.sidebar:
    st.header("Status")
    st.write("metrics:", "✅" if metrics is not None and len(metrics) else "❌")
    st.write("events:", "✅" if events is not None and len(events) else "❌")
    st.write("window:", f"±{WINDOW_SEC}s")

    st.divider()
    st.header("Controls")
    auto_refresh = st.checkbox("Auto refresh (manual reload alternative)", value=False)
    st.caption("자동 갱신은 환경에 따라 부담이 있을 수 있어 체크 해제 권장")

if metrics is None or len(metrics) == 0:
    st.warning("logs/metrics.csv가 없습니다. 먼저 pc_rca_monitor.py를 실행해 metrics를 쌓아주세요.")
    st.stop()

# ===== 지표 요약 =====
c1, c2, c3 = st.columns(3)
c1.metric("Metrics rows", len(metrics))
c2.metric("Time range start", str(metrics["timestamp"].min()))
c3.metric("Time range end", str(metrics["timestamp"].max()))

# ===== CPU / MEM 추이 그래프 =====
st.subheader("CPU / MEM trend")

fig = plt.figure()
plt.plot(metrics["timestamp"], metrics["cpu_pct"], label="cpu_pct")
plt.plot(metrics["timestamp"], metrics["mem_pct"], label="mem_pct")
plt.legend()
plt.xlabel("time")
plt.ylabel("percent")
st.pyplot(fig)

# ===== 이벤트 테이블 =====
st.subheader("Events")

if events is None or len(events) == 0:
    st.info("events.csv가 아직 없거나 이벤트가 없습니다. (이상 감지 미발생)")
    st.stop()

events_view = events.copy()
events_view["top_processes"] = events_view["top_processes"].fillna("")
st.dataframe(events_view, use_container_width=True)

# ===== 이벤트 선택 =====
st.subheader("Event detail (pre/post window)")

event_idx = st.number_input(
    "Select event row index (0-based)",
    min_value=0,
    max_value=max(0, len(events)-1),
    value=min(0, len(events)-1),
    step=1
)

ev = events.iloc[int(event_idx)]
t = ev["timestamp"]

st.write("**timestamp:**", t)
st.write("**event_type:**", ev.get("event_type", ""))
st.write("**cpu_pct:**", ev.get("cpu_pct", ""))
st.write("**cpu_ewma:**", ev.get("cpu_ewma", ""))
st.write("**cpu_std:**", ev.get("cpu_std", ""))
st.write("**z_score:**", ev.get("z_score", ""))
st.write("**z_threshold:**", ev.get("z_threshold", ""))
st.write("**top_processes:**", ev.get("top_processes", ""))

start = t - timedelta(seconds=WINDOW_SEC)
end = t + timedelta(seconds=WINDOW_SEC)

win = metrics[(metrics["timestamp"] >= start) & (metrics["timestamp"] <= end)].copy()

if len(win) == 0:
    st.warning("선택한 이벤트 주변 구간에 metrics 데이터가 없습니다.")
else:
    st.write(f"Window rows: {len(win)} ({start} ~ {end})")

    fig2 = plt.figure()
    plt.plot(win["timestamp"], win["cpu_pct"], label="cpu_pct")
    plt.axvline(t, linestyle="--", label="event_time")
    plt.legend()
    plt.xlabel("time")
    plt.ylabel("cpu_pct")
    st.pyplot(fig2)

if auto_refresh:
    st.rerun()
