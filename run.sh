#!/bin/bash
sudo pigpiod

until (/home/pi/weather-station/weather_station_byo.py);
do
echo "Program exited! Restarting weather station in 10 seconds..."
sleep 10s # wait 
done;
