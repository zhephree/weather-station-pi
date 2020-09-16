import twitter
import datetime
import decimal
import math

api = twitter.Api(consumer_key="EDxLdDwX39TgU7NgTm2LxIPPz",
                  consumer_secret="VpkUNuTgr6p3EgcOwfMLQB9ggXvJZvBkNkjo0SqJJm5KEFSpSn",
                  access_token_key="1273480499227435008-sBHRINEhRFLRa8WdDNR3K3rd2AHCo2",
                  access_token_secret="DSU9MbbDiQdhpIYWYxyenfpwDzAnWn31xT7Mz9aWxa8Pt")

def cToF(temp):
    return round((float(temp) * float(9/5)) + float(32), 2)

def kphToMph(speed):
    return round(float(speed) / float(1.609), 2)

def mmToIn(mm):
    return round(float(mm) / 25.4, 3)

def degToDirection(deg):
    if deg >= 0 and deg < 22.5:
        return "S"
    elif deg >= 22.5 and deg < 45:
        return "SSE"
    elif deg >= 45 and deg < 67.5:
        return "SE"
    elif deg >= 67.5 and deg < 90:
        return "ESE"
    elif deg >= 90 and deg < 112.5:
        return "E"
    elif deg >= 112.5 and deg < 135:
        return "ENE"
    elif deg >= 135 and deg < 157.5:
        return "NE"
    elif deg >= 157.5 and deg < 180:
        return "NNE"
    elif deg >= 180 and deg < 202.5:
        return "N"
    elif deg >= 202.5 and deg < 225:
        return "NNW"
    elif deg >= 225 and deg < 247.5:
        return "NW"
    elif deg >= 247.5 and deg < 270:
        return "WNW"
    elif deg >= 270 and deg < 292.5:
        return "W"
    elif deg >= 292.5 and deg < 315:
        return "WSW"
    elif deg >= 315 and deg < 337.5:
        return "SW"
    elif deg >= 337.5:
        return "SSW"
    
def degToDirectionINVERTED(deg):
    if deg >= 0 and deg < 22.5:
        return "N"
    elif deg >= 22.5 and deg < 45:
        return "NNW"
    elif deg >= 45 and deg < 67.5:
        return "NW"
    elif deg >= 67.5 and deg < 90:
        return "WNW"
    elif deg >= 90 and deg < 112.5:
        return "W"
    elif deg >= 112.5 and deg < 135:
        return "WSW"
    elif deg >= 135 and deg < 157.5:
        return "SW"
    elif deg >= 157.5 and deg < 180:
        return "SSW"
    elif deg >= 180 and deg < 202.5:
        return "S"
    elif deg >= 202.5 and deg < 225:
        return "SSE"
    elif deg >= 225 and deg < 247.5:
        return "SE"
    elif deg >= 247.5 and deg < 270:
        return "ESE"
    elif deg >= 270 and deg < 292.5:
        return "E"
    elif deg >= 292.5 and deg < 315:
        return "ENE"
    elif deg >= 315 and deg < 337.5:
        return "NE"
    elif deg >= 337.5:
        return "NNE"

def calculateFeelsLike(temp, rh, wind):
    temp_sq = float(temp * temp)
    rh_sq = float(rh * rh)
    temp = float(temp)
    rh = float(rh)
    wind = float(wind)

    if temp >= 70:
        feels_like = round(float(-42.379) + (float(2.04901523) * temp) + (float(10.14333127) * rh) + (float(-0.22475541) * temp * rh) + (float(-6.83783E-3) * temp_sq) + (float(-5.481717E-2) * rh_sq) + (float(1.22874E-3) * temp_sq * rh) + (float(8.5282E-4) * temp * rh_sq) + (float(-1.99E-6) * temp_sq * rh_sq), 2)
    else:
        feels_like = round(float(35.74) + (float(0.6215) * temp) - (float(35.75) * wind) + (float(0.4275) * temp * wind), 2)

    return feels_like

def calculateDewPoint(t, rh):
    t = float(t)
    rh = float(rh)
    return round(float(243.04) * (float(math.log(rh / float(100))) + ((float(17.625) * t) / (float(243.04) + t))) / (float(17.625) - float(math.log(rh / float(100))) - ((float(17.625) * t) / (float(243.04) + t))), 2)

def postTweet(temp, ground_temp, humidity, pressure, wind_speed, wind_direction, rain_data, last_id, test=False):
    now = datetime.datetime.now()
    rain = round(float(rain_data["TOTAL"]), 3)
    est_temp = cToF((temp + ground_temp) / 2)
    
    tweet = now.strftime("%m/%d/%Y %I:%M%p") + "\n\n"
    tweet = tweet + "Temp: " + str(est_temp) + "°\n"
    tweet = tweet + "Ambient Temp: " + str(cToF(temp)) + "°\n"
    tweet = tweet + "Ground Temp: " + str(cToF(ground_temp)) + "°\n"
    tweet = tweet + "Feels Like: " + str(calculateFeelsLike(est_temp, humidity, wind_speed)) + "°\n"
    tweet = tweet + "Humidity: " + str(round(humidity, 2)) + "%\n"
    tweet = tweet + "Pressure: " + str(round(pressure, 2)) + "mb\n"

    if kphToMph(wind_speed) == 0:
        wd = '--'
    else:
        wd = degToDirection(wind_direction)
        
    tweet = tweet + "Wind: " + str(kphToMph(wind_speed)) + "mph " + wd + "\n"
    tweet = tweet + "Dew Point: " + str(calculateDewPoint(est_temp, humidity)) + "°\n"
    tweet = tweet + "Rain Today: " + str((rain)) + "in"
    tweet = tweet + "\n\nhttp://70122weather.com/" + str(last_id)

    if test == False:
        api.PostUpdate(tweet)

    print(tweet)
    print(len(tweet))
