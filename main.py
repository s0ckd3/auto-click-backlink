import time

import settings
from rate_up import RateUp

app = RateUp()

# how long bot will be on page (optional)
app.min_time = settings.MIN_TIME  # default 62 sec
app.max_time = settings.MAX_TIME  # default 146 sec

# generate headers list
headers = app.generate_header_list(2000)

while True:
    try:
        # target urls list
        with open('urls.txt') as f:
            urls = f.read().strip().split('\n')
            app.start(headers, urls)
    except KeyboardInterrupt:
        break
    print('RELOAD AFTER 30s')
    time.sleep(30)
