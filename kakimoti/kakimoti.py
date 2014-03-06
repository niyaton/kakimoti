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

def get_live_e_json():
    return json.loads(urlopen(LIVE_E_NAIST_URL).read().decode('utf8'))

def get_live_e_data_str(livee_json, output_data):
    for key, unit, ndigits in output_data:
        value = round(float(livee_json[key]['value']), ndigits)
        format_str = '{0:.' + str(ndigits) + 'f}({1})'
        yield format_str.format(value, unit)

def get_tweet():
    output_data = [TEMPERATURE, HUMIDITY, PRESSURE, RAINFALL]
    data = get_live_e_json()
    tweet = ','.join(get_live_e_data_str(data, output_data))

    time = dateutil.parser.parse(data[TEMPERATURE[0]]['time'])
    tweet += ' 【' + time.strftime("%Y-%m-%d %H:%M:%S") + '】'

    return tweet

def tweet_current_weather(debug=False):
    tweet = get_tweet()
    if debug:
        print(tweet)
    else:
        twitter = Twython(API_KEY, API_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
        twitter.update_status(status=tweet) 

def check_rain(debug=False):
    rainfalls = read_rainfall_log()

    print(rainfalls)
    data = get_live_e_json()

    rainfall = float(data[RAINFALL[0]]['value'])
    rainfall_time = data[RAINFALL[0]]['time']
    rainfalls.append((str(rainfall), rainfall_time))

    if len(rainfalls) == 1:
        write_rainfall_log(rainfalls)
        return

    prev = float(rainfalls[0][0])
    raining = is_raining(prev, rainfall)
    time_str = dateutil.parser.parse(rainfall_time).strftime("%Y-%m-%d %H:%M:%S") 
    if raining == "START":
        strs = []
        strs = ["【start raining】"]
        strs.append(str(round(rainfall, 1)))
        strs.append(time_str)
        tweet = "【start raining】" + ','.join(strs)
        if debug == False:
            twitter = Twython(API_KEY, API_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
            twitter.update_status(status=tweet) 
        else:
            print(tweet)
    elif raining == "STOP":
        strs = ['【stop raining】']
        strs.append(time_str)
        tweet = ''.join(strs)
        if debug == False:
            twitter = Twython(API_KEY, API_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
            twitter.update_status(status=tweet) 
        else:
            print(tweet)

    write_rainfall_log(rainfalls[-1::])

def is_raining(prev, current):
    if prev == 0 and current != 0:
        return "START"
    elif prev != 0 and current == 0:
        return "STOP"
    else:
        return "CONTINUE"

def write_rainfall_log(rainfalls):
    with open('rainfall.log', 'w') as w:
        for rainfall in rainfalls:
            w.write(','.join(rainfall))
            w.write('\n')

def read_rainfall_log():
    with open('rainfall.log') as f:
        return [ line.rstrip().split(',') for line in f.readlines() ]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Yet Another bot for weathercast at NAIST')
    parser.add_argument('--debug', '-d', action='store_true', help='debug flag')
    parser.add_argument('--check-rain', '-r', action='store_true', help='check start rainning')

    args = parser.parse_args()

    if args.check_rain:
        check_rain(args.debug)
    else:
        tweet_current_weather(args.debug)
