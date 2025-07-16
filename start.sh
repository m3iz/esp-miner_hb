#!/bin/bash
sudo /home/orangepi/Documents/heatbit/esp-miner-emberone-miner/venv/bin/python3 /home/orangepi/Documents/heatbit/esp-miner-emberone-miner/pyminer.py -o stratum+tcp://ru-west.stratum.braiins.com:3333 -d -P -u tmminty.$1 -p 123 -c /home/orangepi/Documents/heatbit/esp-miner-emberone-miner/config.yml
