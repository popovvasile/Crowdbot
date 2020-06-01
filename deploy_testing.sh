#! /usr/bin/env sh
set -e
#cd ..
source venv/bin/activate
export SHOP_PRODUCTION=0
export BOTFATHER_TOKEN=892372248:AAEM32Ye0ye4rTkyTuk5Z4minhsNKVhSQ-w
cd crowdrobot
killall python
nohup python crowdrobot_alive_checker.py &
nohup python rest_api/crowdbot_rest_api.py &
nohup python rest_api/face.py &
cd ..
cd botfather
nohup python runner.py &
