import psutil
import pandas as pd
import datetime

print("현재 시간:", datetime.datetime.now())
print("CPU 사용률:", psutil.cpu_percent(interval=1), "%")
print("메모리 사용률:", psutil.virtual_memory().percent, "%")



