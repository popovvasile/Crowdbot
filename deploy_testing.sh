#! /usr/bin/env sh
#set -e
cd ..
source venv/bin/activate
export SHOP_PRODUCTION=0
export BOTFATHER_TOKEN=804642806:AAEJ_YHVzfbRUTG_mzKcxL2lcKZE9K6h2HY
cd crowdrobot
killall python
nohup python crowdrobot_alive_checker.py &
nohup python rest_api/crowdbot_rest_api.py &
nohup python rest_api/fake.py &
cd ..
cd bot-father
nohup python runner.py &

