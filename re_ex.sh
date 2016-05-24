sh stop_ex.sh
find -name "*.log" | xargs rm -rf
git stash
git pull
sh start_ex.sh