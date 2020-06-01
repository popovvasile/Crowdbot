#! /usr/bin/env sh
set -e
exec "pkill" "-9" "python"
export SHOP_PRODUCTION=1
export BOTFATHER_TOKEN=892372248:AAEM32Ye0ye4rTkyTuk5Z4minhsNKVhSQ-w
cd crowdrobot
exec "nohup" "python" "crowdrobot_alive_checker.py" "&"
exec "nohup" "python" "rest_api/crowdbot_rest_api.py" "&"
cd ..
cd botfather
exec "nohup" "python" "runner.py" "&"
