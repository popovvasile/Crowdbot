#! /usr/bin/env sh
set -e

export SHOP_PRODUCTION=1
export BOTFATHER_TOKEN=892372248:AAEM32Ye0ye4rTkyTuk5Z4minhsNKVhSQ-w
cd crowdrobot
killall python
nohup python crowdrobot_alive_checker.py &
nohup python rest_api/crowdbot_rest_api.py &
cd ..
cd botfather
nohup python runner.py &
