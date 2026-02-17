# PC RCA Monitor (CPU Anomaly Detection + Root Cause)

실시간으로 PC/서버의 **CPU 이상(Anomaly)**을 감지하고, 그 시점의 **Top 프로세스(원인 후보)**를 기록해
“언제부터 느려졌는지(현상)” + “왜 느려졌는지(원인 후보)”를 빠르게 파악하는 프로젝트입니다.

## Features
- 실시간 지표 수집: CPU%, MEM% → `logs/metrics.csv`
- 이상 감지:
  - EWMA 기반 (초기 버전)
- 원인 후보 식별: CPU Top 프로세스 스냅샷
- 이벤트 기록: `logs/events.csv`
- 자동 리포트 생성(Markdown): `reports/pc_rca_report.md`
- (추가 예정) Streamlit 대시보드

## Project Structure
- pc_rca_monitor.py # 실시간 수집 + 이상 감지 + 이벤트 기록
- generate_report.py # events/metrics 기반 자동 리포트 생성
- analyze_events.py # 이벤트 전후 구간 비교 분석
- reports/pc_rca_report.md # 자동 생성 리포트 (예시)
- logs/ # 실행하면 생성되는 로그 (깃에는 올리지 않음)

## Setup (Linux / GCP VM)
> Python venv(가상환경)에서 실행하는 것을 권장합니다.

# (1) 가상환경 생성/활성화
python3 -m venv rca_env
source rca_env/bin/activate

# (2) 패키지 설치
pip install -U pip
pip install psutil pandas streamlit matplotlib

## Run

# (1) 모니터링 실행
source rca_env/bin/activate
python pc_rca_monitor.py
- Ctrl + C로 종료
- 실행하면 logs/metrics.csv, logs/events.csv가 저장

# (2) 분석 (이벤트 전후 비교)
source rca_env/bin/activate
python analyze_events.py

- 현상(증상) 수집: CPU/MEM을 일정 주기로 저장
- 이상 감지: “평소 대비 얼마나 벗어났는지”를 점수화(EWMA)
- 원인 후보: 이상 시점의 CPU Top 프로세스 기록
- 리포트: 이상 시점 전후 구간 비교로 “스파이크 vs 지속부하” 판단 근거 제공

## Note
- logs/는 데이터가 계속 쌓이므로 GitHub에는 커밋하지 않습니다. (.gitignore로 제외)
- 프로세스 CPU%는 샘플링 타이밍에 영향을 받으므로, 수집 주기와 워밍업 로직이 중요합니다.