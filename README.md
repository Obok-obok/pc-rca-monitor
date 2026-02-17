# PC RCA Monitor  
Real-Time CPU Anomaly Detection & Root Cause Analysis Dashboard

---

## 📌 Overview

PC RCA Monitor는 실시간 시스템 지표(CPU/MEM)를 수집하고  
통계 기반 이상 감지(EWMA + Z-score)를 통해 성능 저하 이벤트를 탐지하며,  
해당 시점의 Top 프로세스를 기록하여 Root Cause를 식별하는 프로젝트입니다.

이 프로젝트는 다음을 목표로 합니다:

- "언제 느려졌는가?" (현상 감지)
- "왜 느려졌는가?" (원인 후보 식별)
- "그 이후 어떻게 변했는가?" (전후 비교 분석)

---

## 🚀 Features

- 실시간 CPU / MEM 수집 (`psutil`)
- EWMA 기반 평균 추정
- Z-score 기반 이상 감지
- 이상 발생 시 Top 프로세스 스냅샷 기록
- 자동 Markdown 리포트 생성
- Streamlit 대시보드 시각화
- GCP Compute Engine 환경 배포

---

## 🏗 System Architecture

```
[System Metrics Collection]
        ↓
[EWMA / Z-score Anomaly Detection]
        ↓
[Top Process Snapshot]
        ↓
[Event Log + Markdown Report]
        ↓
[Streamlit Dashboard Visualization]
```

---

## 📂 Project Structure

```
pc_rca_monitor.py         # 실시간 수집 + 이상 감지
generate_report.py        # 자동 Markdown 리포트 생성
analyze_events.py         # 이벤트 전후 구간 분석
app.py                    # Streamlit 대시보드
reports/                  # 자동 생성 리포트
logs/                     # metrics / events 로그 (git 제외)
docs/screenshots/         # README 데모 이미지
```

---

## ⚙️ Setup

### 1️⃣ 가상환경 생성

```bash
python3 -m venv rca_env
source rca_env/bin/activate
```

### 2️⃣ 패키지 설치

```bash
pip install -U pip
pip install psutil pandas streamlit matplotlib
```

---

## ▶️ Run

### 실시간 모니터 실행

```bash
source rca_env/bin/activate
python pc_rca_monitor.py
```

로그 생성:
- `logs/metrics.csv`
- `logs/events.csv`

---

### 리포트 생성

```bash
python generate_report.py
```

결과:
```
reports/pc_rca_report.md
```

---

### Streamlit 대시보드 실행

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

브라우저 접속:
```
http://<VM_IP>:8501
```

---

## 📸 Demo

### Dashboard Overview

![Dashboard Overview](docs/screenshots/dashboard_overview.png)

- CPU / MEM 시계열 그래프
- 이상 이벤트 테이블
- 이벤트 선택 시 전후 구간 시각화

---

### Event Detail View

![Event Detail](docs/screenshots/event_detail.png)

- 점선: 이상 감지 시점
- 전후 ±60초 CPU 비교
- Top 프로세스 기반 Root Cause 후보 확인

---

## 📊 Example Event Log

```csv
timestamp,event_type,cpu_pct,cpu_ewma,threshold,top_processes
2026-02-15 03:21:34,CPU_ANOMALY,55.5,14.48,44.75,python(19000) cpu=99.9
```

### 해석

- 평소 평균 CPU ≈ 14%
- 이벤트 순간 CPU ≈ 55%
- PID 19000 python 프로세스가 CPU 99.9% 점유

→ 명확한 Root Cause 식별

---

## 📈 Example RCA Interpretation

| Event Time | CPU | Before Avg | After Avg | Root Cause |
|------------|------|------------|------------|------------|
| 03:21:34 | 55.5% | 2.39% | 49.85% | python(19000) |

- 이벤트 직전 정상 상태
- 이벤트 이후 지속적 고부하
- 단순 스파이크가 아닌 지속 부하 유형

---

## 🧠 Anomaly Detection Model

### EWMA (Exponential Weighted Moving Average)

평균을 실시간으로 추정하며 최근 데이터에 더 높은 가중치를 둠.

### Z-score 기반 이상 점수

\[
Z = \frac{x - \mu}{\sigma}
\]

- μ: EWMA 평균
- σ: EWMA 기반 분산 추정
- Z > 3 → 통계적으로 드문 이상치

---

## 🛠 Tech Stack

- Python 3.11
- psutil
- pandas
- matplotlib
- Streamlit
- Git / GitHub
- GCP Compute Engine (Free Tier)

---

## 🎯 What This Project Demonstrates

- 실시간 시스템 모니터링
- 통계 기반 이상 감지 모델 구현
- Root Cause Analysis 파이프라인 설계
- 자동 리포트 생성
- 웹 기반 대시보드 구축
- 클라우드 배포

---

## 🔮 Future Improvements

- CPU + MEM + IO 다변량 이상 감지
- Process 기여도 점수 계산
- 자동 RCA 요약 생성 (LLM 연동)
- Docker 이미지화
- GitHub Actions CI/CD

---

## 📌 Author

Obok-obok  
GCP + Python 기반 실시간 이상 감지 & RCA 프로젝트