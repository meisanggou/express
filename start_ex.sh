cd Web
nohup python ex_web.py 1>> log_web.log 2>>log_web.log &
echo $! >> ../service.pid

cd ../API_V1
nohup python ex_api.py 1>> log_api.log 2>>log_api.log &
echo $! >> ../service.pid

cd ../Service
nohup python ex_QueryService.py 1>> log_query.log 2>> log_query.log &
echo $! >> ../service.pid