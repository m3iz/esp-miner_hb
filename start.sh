#!/bin/bash
sudo /home/pi/emberone-miner/venv/bin/python3 /home/pi/emberone-miner/pyminer.py -o stratum+tcp://ru-west.stratum.braiins.com:3333 -d -P -u tmminty.$1 -p 123 -c /home/pi/emberone-miner/config.$1.yml
