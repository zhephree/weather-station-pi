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

tweet.postTweet(last_data['AMBIENT_TEMPERATURE'], last_data['GROUND_TEMPERATURE'], last_data['HUMIDITY'], last_data['AIR_PRESSURE'], last_data['WIND_SPEED'], last_data['WIND_SPEED'], rain_data, last_id, True)


