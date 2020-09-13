pwd=$(dirname $0)

sh $pwd/purge_task_queue.sh
service data_cube_ui restart