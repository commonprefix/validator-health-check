import time
import check_health

while True:
  check_health.check()
  time.sleep(60)