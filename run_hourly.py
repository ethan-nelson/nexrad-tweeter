import datetime as dtm
import time
import pyart

while True:
    dt = dtm.datetime.now() + dtm.timedelta(hours=1)
    dt = dt.replace(minute=2)
    while dtm.datetime.now() < dt:
        time.sleep(60)
        print 'Trying again in 60 seconds.'
    execfile('./hourly.py')
