import database
import tweet
import time
from datetime import date
from datetime import datetime

db = database.remote_mysql_database()
db.reconnect()
