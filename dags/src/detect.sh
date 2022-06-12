cd /opt/airflow/yolov5 && ls

python detect.py --weights ./exp/weights/best.pt --source ../download_video.mp4 --conf 0.5 --data data/opgg.yaml --line-thickness 1