import time
import datetime
from datetime import timedelta
import ccs811 as css

aqm = ccs.CCS811()
aqm.setup()

while True:
    current_time = datetime.datetime.utcnow()
    sensorTime = current_time.strftime('%Y-%m-%d %H:%M:%S')

    try:
        if aqm.data_available():
            aqm.read_logorithm_results()
            eco2 = aqm.CO2
            tvoc = aqm.tVOC
        elif aqm.check_for_error():
            aqm.print_error()
    except Exception as ex:
        print("Error condition detected reading CCS811 sensor: ", sys.exc_info()[0])
        
