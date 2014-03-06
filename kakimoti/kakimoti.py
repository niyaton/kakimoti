from urllib.request import urlopen
from twython import Twython
import json
import dateutil.parser
import datetime
from secret import API_KEY, API_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET

LIVE_E_NAIST_URL = 'http://live-e.naist.jp/naist/?data=json'
LIVEDOOR_WEATHER_URL ='http://weather.livedoor.com/forecast/webservice/json/v1?city=290010'
TEMPERATURE = ('Temperature', '℃', 1)
HUMIDITY = ('Humidity', '%', 0)
PRESSURE = ('Pressure', 'hPa', 1)
RAINFALL = ('Rainfall', 'mm/h', 1)
#WINDIR = ('WinDir', 'mm/h')
#WINDSPEED = 'WindSpeed'

def get_live_e_json():
    return json.loads(urlopen(LIVE_E_NAIST_URL).read().decode('utf8'))

def get_nara_forecast():
    return json.loads(urlopen(LIVEDOOR_WEATHER_URL).read().decode('utf8'))

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

def forecast(debug=False):
    now = datetime.datetime.now()
    data = get_nara_forecast()
    if now.hour < 12:
        tweet = get_tweet_for_morning(data)
    else:
        tweet = get_tweet_for_evening(data)

    if debug == False:
        twitter = Twython(API_KEY, API_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
        twitter.update_status(status=tweet) 
    else:
        print(tweet)

def get_tweet_for_morning(data):
    weather = data['forecasts'][0]
    tweet_format = 'おはようございます。今日の天気は{0}の予定です。 [{1}]'
    return tweet_format.format(weather['telop'], get_pinpoint_forecast_url(data))

def get_tweet_for_evening(data):
    weather = data['forecasts'][1]
    tweet_format = '明日の天気は{0}の予定です。最高気温は{1}℃、最低気温は{2}℃の予定です。[{3}]'
    temp_min = float(weather['temperature']['min']['celsius'])
    temp_max = float(weather['temperature']['max']['celsius'])
    return tweet_format.format(weather['telop'], temp_max, temp_min, get_pinpoint_forecast_url(data))

def get_pinpoint_forecast_url(data):
     ikoma_index = [ i['name'] for i in data['pinpointLocations']].index('生駒市')
     return data['pinpointLocations'][ikoma_index]['link']

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Yet Another bot for weathercast at NAIST')
    parser.add_argument('--debug', '-d', action='store_true', help='debug flag')
    parser.add_argument('--check-rain', '-r', action='store_true', help='check start rainning')
    parser.add_argument('--forecast', '-f', action='store_true', help='tweetforecast')

    args = parser.parse_args()

    if args.check_rain:
        check_rain(args.debug)
    elif args.forecast:
        forecast(args.debug)
    else:
        tweet_current_weather(args.debug)
