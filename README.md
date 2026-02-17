# PC RCA Monitor  
Real-Time CPU Anomaly Detection & Root Cause Analysis Dashboard

---

## 📌 Overview

PC RCA Monitor는 실시간 시스템 지표(CPU/MEM)를 수집하고  
통계 기반 이상 감지(EWMA + Z-score)를 통해 성능 저하 이벤트를 탐지하며,  
해당 시점의 Top 프로세스를 기록하여 Root Cause를 식별하는 프로젝트입니다.

이 프로젝트는 다음 질문에 답하기 위해 설계되었습니다:

- 언제부터 느려졌는가? (현상 감지)
- 왜 느려졌는가? (원인 후보 식별)
- 그 이후 어떻게 변했는가? (전후 비교 분석)

---

## 🚀 Features

- 실시간 CPU / MEM 수집 (`psutil`)
- EWMA 기반 평균 추정
- EWMA 기반 분산 추정
- Z-score 기반 이상 감지
- 이상 발생 시 Top 프로세스 스냅샷 기록
- 자동 Markdown 리포트 생성
- Streamlit 대시보드 시각화
- GCP Compute Engine 배포

---

## 🏗 System Architecture

```
[System Metrics Collection]
        ↓
[EWMA Mean & Variance Estimation]
        ↓
[Z-score Anomaly Detection]
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
pc_rca_monitor.py         # 실시간 수집 + Z-score 이상 감지
generate_report.py        # 자동 Markdown 리포트 생성
analyze_events.py         # 이벤트 전후 구간 분석
app.py                    # Streamlit 대시보드
requirements.txt
reports/                  # 자동 생성 리포트
logs/                     # metrics / events 로그 (git 제외)
```

---

## 📊 Anomaly Detection Model

### EWMA (Exponential Weighted Moving Average)

최근 데이터에 더 높은 가중치를 두어 평균을 실시간으로 추정합니다.

```
new_mean = α * x + (1-α) * prev_mean
```

### EWMA 기반 분산 추정

```
diff = x - mean
var = α * (diff²) + (1-α) * prev_var
```

### Z-score 계산

\[
Z = \frac{x - \mu}{\sigma}
\]

- μ : EWMA 평균
- σ : EWMA 기반 표준편차
- Z > 3 → 통계적으로 드문 이상치

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
pip install -r requirements.txt
```

또는 직접:

```bash
pip install psutil pandas matplotlib streamlit
```

---

## ▶️ Run

### 실시간 모니터 실행

```bash
source rca_env/bin/activate
python pc_rca_monitor.py
```

생성 파일:
- logs/metrics.csv
- logs/events.csv

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
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

---

## 🌐 Live Demo

<a href="https://your-app-name.streamlit.app" target="_blank">
  <img src="https://img.shields.io/badge/Streamlit-Live%20Demo-brightgreen?logo=streamlit" />
</a>

<a href="https://your-app-name.streamlit.app" target="_blank">
  👉 Open Live Dashboard
</a>



[![Open App](https://img.shields.io/badge/Streamlit-Live%20Demo-brightgreen?logo=streamlit)](https://pc-rca-monitor-pa6hbqdyhyfwaeqyyk3va7.streamlit.app/)

🔗 **[Open Streamlit Dashboard](https://pc-rca-monitor-pa6hbqdyhyfwaeqyyk3va7.streamlit.app/)**

외부 IP 확인:

```bash
gcloud compute instances describe free-vm --zone us-central1-a \
  --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

```bash
http://<VM_EXTERNAL_IP>:8501/
```

### ⚠ 참고

- VM이 Running 상태여야 합니다.
- 방화벽에서 tcp:8501 포트가 열려 있어야 합니다.
- Stop/Start 시 외부 IP가 변경될 수 있습니다.

---

## 📈 Example RCA Interpretation

| Event Time | CPU | Z-score | Root Cause |
|------------|------|----------|------------|
| 03:21:34 | 55.5% | 4.82 | python(19000) |

해석:

- 평소 평균 대비 통계적으로 유의미한 급등
- 특정 python 프로세스가 CPU 99% 점유
- 단순 스파이크가 아닌 지속 부하 유형

---

## 🛠 Tech Stack

- Python 3.11
- psutil
- pandas
- matplotlib
- Streamlit
- Git / GitHub
- Google Cloud Platform (Compute Engine)

---

## 🔮 Future Improvements

- CPU + MEM + IO 다변량 이상 감지
- Process 기여도 점수 계산
- 자동 RCA 요약 생성 (LLM 연동)
- Docker 이미지화
- GitHub Actions CI/CD

---

## 🎯 What This Project Demonstrates

- 실시간 시스템 모니터링 설계
- 통계 기반 이상 감지 모델 구현
- Root Cause Analysis 파이프라인 구축
- 자동 리포트 생성 시스템
- 웹 기반 대시보드 구현
- 클라우드 환경 배포 경험

---

## 👤 Author

Obok-obok  
Python + GCP 기반 실시간 이상 감지 & RCA 프로젝트