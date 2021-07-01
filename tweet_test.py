import database
import tweet
import time
from datetime import date
from datetime import datetime

db = database.mysql_database()


results = db.query("SELECT * FROM WEATHER_MEASUREMENT ORDER BY `TIMESTAMP` DESC LIMIT 1")
last_data = results[0]

now = time.time()
print(now)
today = date.today()
midnight = datetime.combine(today, datetime.min.time()).timestamp()
print(midnight)
rain_results = db.query("SELECT (SUM(RAINFALL) / 25.4) AS TOTAL FROM WEATHER_MEASUREMENT WHERE `TIMESTAMP` >= " + str(midnight) + " AND `TIMESTAMP` <= " + str(now))
rain_data = rain_results[0]
del db

print(rain_results[0])

db = database.remote_mysql_database()
id_results = db.query("SELECT ID FROM WEATHER_MEASUREMENT ORDER BY `TIMESTAMP` DESC LIMIT 1")
id_data = id_results[0]
last_id = id_data["ID"]
del db

tweet.postTweet(float(last_data['AMBIENT_TEMPERATURE']), float(last_data['GROUND_TEMPERATURE']), float(last_data['HUMIDITY']), float(last_data['AIR_PRESSURE']), float(last_data['NEW_WIND_SPEED']), float(last_data['NEW_WIND_SPEED']), rain_data, last_id, True)


tweet.postLightningTweet(3335, 6, True)
