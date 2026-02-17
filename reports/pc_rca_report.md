# PC RCA 자동 리포트 (Z-score)

- metrics rows: 791
- events rows: 4
- metrics time range: 2026-02-14 22:28:27 ~ 2026-02-17 14:52:44
- window: ±30s

## 이벤트 요약

| # | timestamp | cpu | ewma | std | z | z_th | cpu_before(30s avg) | cpu_after(30s avg) | top_processes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 2026-02-17 14:50:32 | 6.90 | 2.91 | 1.99 | 2.00 | 2.00 | 1.64 | 13.13 | python(1676) cpu=1.5; systemd(1) cpu=0.5; khugepaged(36) cpu=0.5 |
| 2 | 2026-02-17 14:50:34 | 26.90 | 7.71 | 8.76 | 2.19 | 2.00 | 2.03 | 11.29 | node(979) cpu=34.0; code-c3a26841a84f20dfe0850d0a5a9bd01da4f003ea(1886) cpu=5.8; kswapd0(42) cpu=1.5 |
| 3 | 2026-02-17 14:50:36 | 62.20 | 18.61 | 21.01 | 2.07 | 2.00 | 3.65 | 7.08 | node(979) cpu=50.9; node(1937) cpu=41.4; code-c3a26841a84f20dfe0850d0a5a9bd01da4f003ea(1886) cpu=9.9 |
| 4 | 2026-02-17 14:52:09 | 66.00 | 15.24 | 22.72 | 2.23 | 2.00 | 2.46 | 23.70 | node(1937) cpu=51.3; kswapd0(42) cpu=3.0; node(1012) cpu=1.0 |

## 해석 가이드

- **z**가 **z_th**를 넘으면: 평소 대비 통계적으로 드문 CPU 상승(이상)으로 판단
- **cpu_before**가 낮고 이벤트 순간 **cpu**가 높으면: 스파이크/이상 발생 시점으로 해석
- **cpu_after**가 높게 유지되면: 단발성 스파이크가 아닌 지속 부하 가능성
- **top_processes**에서 높은 CPU를 점유한 PID가 Root Cause 후보