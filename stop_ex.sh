cat service.pid | while read line
do
    kill -9 $line
done
rm -f service.pid
