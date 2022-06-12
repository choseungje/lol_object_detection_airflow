cd /opt/airflow/yolov5 && ls
python train.py --img 640 --batch 128 --epoch 1 --data opgg.yaml --project ./ --worker 0
