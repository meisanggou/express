cd Web
nohup python ex_web.py 1>> ex_web.log 2>>ex_web.log &
echo $! >> ../service.pid

cd ../API_V1
nohup python run.py 1>> api.log 2>>api.log &
echo $! >> ../service.pid

cd ../Service
nohup python QueryService.py 1>> query_service.log 2>> query_service.log &
echo $! >> ../service.pid