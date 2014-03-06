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

def get_live_e_data_str(livee_json, output_data):
    for key, unit, ndigits in output_data:
        value = round(float(livee_json[key]['value']), ndigits)
        format_str = '{0:.' + str(ndigits) + 'f}({1})'
        yield format_str.format(value, unit)

def get_tweet():
    output_data = [TEMPERATURE, HUMIDITY, PRESSURE, RAINFALL]
    data = json.loads(urlopen(LIVE_E_NAIST_URL).read().decode('utf8'))

    tweet = ','.join(get_live_e_data_str(data, output_data))

    time = dateutil.parser.parse(data[TEMPERATURE[0]]['time'])
    tweet += ' 【' + time.strftime("%Y-%m-%d %H:%M:%S") + '】'

    return tweet
 
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Yet Another bot for weathercast at NAIST')
    parser.add_argument('--debug', '-d', action='store_true', help='debug flag')

    args = parser.parse_args()

    tweet = get_tweet()

    if args.debug:
        print(tweet)
    else:
        twitter = Twython(API_KEY, API_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
        twitter.update_status(status=tweet)
