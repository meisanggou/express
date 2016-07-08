cd Web
nohup python -u ex_web.py 1>> log_web.log 2>>log_web.log &
echo $! >> ../service.pid

cd ../Service
nohup python -u ex_QueryService.py 1>> log_query.log 2>> log_query.log &
echo $! >> ../service.pid