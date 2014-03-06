from urllib.request import urlopen
from twython import Twython
import json
import dateutil.parser
from secret import API_KEY, API_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET

LIVE_E_NAIST_URL = 'http://live-e.naist.jp/naist/?data=json'
TEMPERATURE = ('Temperature', '℃', 1)
HUMIDITY = ('Humidity', '%', 0)
PRESSURE = ('Pressure', 'hPa', 1)
RAINFALL = ('Rainfall', 'mm/h', 1)
#WINDIR = ('WinDir', 'mm/h')
#WINDSPEED = 'WindSpeed'

output_data = [TEMPERATURE, HUMIDITY, PRESSURE, RAINFALL]

data = json.loads(urlopen(LIVE_E_NAIST_URL).read().decode('utf8'))
print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))

time = dateutil.parser.parse(data[TEMPERATURE[0]]['time'])

#temperature = data[TEMPERATURE]

def get_live_e_data_str():
    for key, unit, ndigits in output_data:
        value = round(float(data[key]['value']), ndigits)
        format_str = '{0:.' + str(ndigits) + 'f}({1})'
        yield format_str.format(value, unit)

tweet = ','.join(get_live_e_data_str())
tweet += ' 【' + time.strftime("%Y-%m-%d %H:%M:%S") + '】'

#twitter = Twython(API_KEY, API_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
#twitter.update_status(status=tweet)
print(tweet)

