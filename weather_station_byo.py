#!/usr/bin/python3
from gpiozero import Button
import math
import time
import bme280_sensor
import wind_direction_byo
import statistics
import ds18b20_therm
import database
import tweet
from datetime import date
from datetime import datetime
from RPi_AS3935 import RPi_AS3935
import RPi.GPIO as GPIO

BUCKET_SIZE = 0.2794
rain_count = 0
lightning_count = 0
store_speeds = []
store_directions = []
wind_count = 0
radius_cm = 9.0
wind_interval = 5
interval = 5 * 60
CM_IN_A_KM = 10000.0
CM_IN_A_MI = 160934.0
SECS_IN_AN_HOUR = 3600
ADJUSTMENT = 1.18
gust = 0
tweet_interval = (30 * 60) / interval
interval_count = 0
last_alert = datetime.min
strikes_since_last_alert = 0



def spin():
    global wind_count
    wind_count = wind_count + 1
    #print(wind_count)

def calculate_speed(time_sec):
    global wind_count
    global gust

    circumference_cm = (2 * math.pi) * radius_cm
    rotations = wind_count / 2.0

    #print("rotations:", rotations)

    dist_cm = circumference_cm * rotations
    dist_km = (dist_cm) / CM_IN_A_KM
    dist_mi = (dist_cm) / CM_IN_A_MI

    cm_per_sec = dist_cm / time_sec
    km_per_sec = dist_km / time_sec
    mi_per_sec = dist_mi / time_sec
    cm_per_hour = cm_per_sec * SECS_IN_AN_HOUR
    km_per_hour = km_per_sec * SECS_IN_AN_HOUR
    mi_per_hour = mi_per_sec * SECS_IN_AN_HOUR

    final_speed = km_per_hour * ADJUSTMENT

    return final_speed

def reset_wind():
    global wind_count
    wind_count = 0

wind_speed_sensor = Button(5)
wind_speed_sensor.when_pressed = spin

def bucket_tipped():
    global rain_count
    rain_count +=1
    #print(count * BUCKET_SIZE)

def reset_rainfall():
    global rain_count
    rain_count = 0

rain_sensor = Button(6)
rain_sensor.when_pressed = bucket_tipped

def lightning_strike(channel):
    global lightning_count
    global last_alert
    global strikes_since_last_alert
    global lightning_sensor
    current_timestamp = datetime.now()
    time.sleep(0.003)
    reason = lightning_sensor.get_interrupt()
    print("[LIGHTNING] Interrupt triggered. Reason: " + str(reason))
    if reason == 0x01:
        print("[LIGHTNING] Noise level too high -- adjusting")
        lightning_sensor.raise_noise_floor()
    elif reason == 0x04:
        print("[LIGHTNING] Disturber detected. Masking subsequent disturbers")
        lightning_sensor.set_mask_disturber(True)
    elif reason == 0x08:
        print("[LIGHTNING] Strike detected! (%s)" % current_timestamp.strftime('%H:%M:%S - %Y/%m/%d'))
        if (current_timestamp - last_alert).seconds < 300:
            print("[LIGHTNING] Last strike is too recent. Incrementing counter since last alert.")
            strikes_since_last_alert += 1
            #return
        distance = lightning_sensor.get_distance()
        energy = lightning_sensor.get_energy()
        print("[LIGHTNING] Energy: " + str(energy) + " - Distance: " + str(distance) + "km")
        #if strikes_since_last_alert == 0:
        #    noop = ''
        lightning_count += 1
        rawdb = database.mysql_database()
        query = "INSERT INTO LIGHTNING (ENERGY, DISTANCE, `TIMESTAMP`) VALUES(%s, %s, %s);"
        tstamp = time.time()
        params = (energy, distance, tstamp)
        rawdb.execute(query, params)
        del rawdb
        rawdb = database.remote_mysql_database()
        rawdb.execute(query, params)
        del rawdb
        #else:
        #    strikes_since_last_alert = 0
    if (current_timestamp - last_alert).seconds > 1800 and last_alert != datetime.min:
        strikes_since_last_alert = 0
        last_alert = datetime.min
        

def reset_lightning():
    global lightning_count
    lightning_count = 0

GPIO.setmode(GPIO.BCM)
pin = 17
lightning_sensor = RPi_AS3935.RPi_AS3935(address=0x03, bus=1)
lightning_sensor.set_indoors(False)
lightning_sensor.set_noise_floor(1)
lightning_sensor.calibrate(tun_cap=0x0d)
lightning_sensor.set_min_strikes(1)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
lightning_sensor.set_mask_disturber(False)
GPIO.add_event_detect(pin, GPIO.RISING, callback=lightning_strike)

temp_probe = ds18b20_therm.DS18B20()

db = database.weather_database()


print('Weather Station initialized. Reading data...')
print('Datbaase will be updated every ' + str(interval / 60) + ' minutes.')
print('Tweets will be posted every ' + str((tweet_interval) * (interval / 60)) + ' minutes.')

while True:
    start_time = time.time()
    interval_count = interval_count + 1

    while time.time() - start_time <= interval:
        wind_start_time = time.time()
        reset_wind()
        #time.sleep(wind_interval)
        while time.time() - wind_start_time <= wind_interval:
            store_directions.append(wind_direction_byo.get_value())
            
        final_speed = calculate_speed(wind_interval)
        store_speeds.append(final_speed)
    wind_average = wind_direction_byo.get_average(store_directions)

    wind_gust = max(store_speeds)
    wind_speed = statistics.mean(store_speeds)
    
    rainfall = rain_count * BUCKET_SIZE
    reset_rainfall()

    ground_temp = temp_probe.read_temp()

    
    humidity, pressure, ambient_temp, ambient_temp_f = bme280_sensor.read_all()

    #humidity = 0
    #pressure = 0
    #ambient_temp = 0
    #ambient_temp_f = 0

    timestamp = time.time()
    
    print(wind_speed, wind_gust, wind_average, rainfall, humidity, pressure, ambient_temp, ambient_temp_f, ground_temp, lightning_count)
    db.insert(ambient_temp, ground_temp, 0, pressure, humidity, wind_average, wind_speed, wind_gust, rainfall, lightning_count, timestamp)

    reset_lightning()
    
    print("Interval: " + str(interval_count))
    if interval_count >= tweet_interval:
        #results = rawdb.query("SELECT * FROM WEATHER_MEASUREMENT ORDER BY `TIMESTAMP` DESC LIMIT 1")
        #last_data = results[0]
        now = time.time()
        today = date.today()
        midnight = datetime.combine(today, datetime.min.time()).timestamp()
        rawdb = database.mysql_database()
        rain_results = rawdb.query("SELECT (SUM(RAINFALL) / 25.4) AS TOTAL FROM WEATHER_MEASUREMENT WHERE `TIMESTAMP` >= " + str(midnight) + " AND `TIMESTAMP` <= " + str(now))
        rain_data = rain_results[0]
        del rawdb

        rawdb = database.remote_mysql_database()
        id_results = rawdb.query("SELECT ID FROM WEATHER_MEASUREMENT ORDER BY `TIMESTAMP` DESC LIMIT 1")
        id_data = id_results[0]
        last_id = id_data["ID"]
        del rawdb
        
        interval_count = 0
        tweet.postTweet(ambient_temp, ground_temp, humidity, pressure, wind_speed, wind_average, rain_data, last_id)
        

        
    store_speeds = []
    store_directions = []
