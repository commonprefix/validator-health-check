import time
import datetime
import check_health

while True:
  check_health.check()
  print(f'Checked for: {datetime.datetime.now()}')
  time.sleep(60)