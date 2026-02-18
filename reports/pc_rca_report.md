# PC RCA 자동 리포트 (Z-score)

- metrics rows: 160
- events rows: 3
- metrics time range: 2026-02-18 01:30:17 ~ 2026-02-18 01:35:38
- window: ±30s

## 이벤트 요약

| # | timestamp | cpu | ewma | std | z | z_th | cpu_before(30s avg) | cpu_after(30s avg) | top_processes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 2026-02-18 01:33:03 | 8.70 | 3.96 | 2.23 | 2.12 | 2.00 | 2.44 | 2.29 | node(1181) cpu=8.4; node(1062) cpu=2.0; node(1041) cpu=1.0 |
| 2 | 2026-02-18 01:34:21 | 52.80 | 12.75 | 17.93 | 2.23 | 2.00 | 2.52 | 16.96 | node(1181) cpu=3.0; node(1062) cpu=0.5; python(1602) cpu=0.5 |
| 3 | 2026-02-18 01:35:16 | 35.10 | 8.96 | 12.06 | 2.17 | 2.00 | 2.04 | 22.90 | node(1181) cpu=4.9; node(1062) cpu=1.5; python(1602) cpu=1.0 |

## 해석 가이드

- **z**가 **z_th**를 넘으면: 평소 대비 통계적으로 드문 CPU 상승(이상)으로 판단
- **cpu_before**가 낮고 이벤트 순간 **cpu**가 높으면: 스파이크/이상 발생 시점으로 해석
- **cpu_after**가 높게 유지되면: 단발성 스파이크가 아닌 지속 부하 가능성
- **top_processes**에서 높은 CPU를 점유한 PID가 Root Cause 후보