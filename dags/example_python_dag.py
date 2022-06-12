from datetime import datetime, timedelta
from textwrap import dedent

from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

default_args = {
    'owner': 'owner-name',
    'depends_on_past': False,
    'email': ['your-email@g.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=15),
}

dag_args = dict(
    dag_id="lol",
    default_args=default_args,
    description='lol champion object detection',
    # schedule_interval=timedelta(minutes=50),
    start_date=datetime(2022, 6, 12),
    tags=['object-detection'],
)


def depedency_check():
    import os
    stream = os.popen('pip list')
    output = stream.read()
    print(output)


def create_train_dataset():
    from src.data import create_dataset
    import os
    import json
    from glob import glob

    if not os.path.exists('./datasets'):
        os.mkdir('./datasets')

        base_path = './dags/src/'
        background_path = base_path + "minimap.png"
        labels_path = base_path + "label/"
        with open(f"{base_path}label/labels.json", "r") as f:
            labels = json.load(f)
        # create_train_data_num = 100000
        # create_valid_data_num = 20000
        create_train_data_num = 100
        create_valid_data_num = 20

        print("\nCreate Train Dataset")
        save_folder = "./datasets/train"
        create_dataset(
            background_path, labels_path, create_train_data_num, labels, save_folder
        )

        print("\nCreate Valid Dataset")
        save_folder = "./datasets/valid"
        create_dataset(
            background_path, labels_path, create_valid_data_num, labels, save_folder
        )
    else:
        print("Already Dataset!")


def youtube_download():
    from pytube import YouTube
    import cv2
    import os
    if not os.path.exists('download_video.mp4'):
        yt = YouTube('https://www.youtube.com/watch?v=HgIREYFDGg8')

        DOWNLOAD_FOLDER = "./"
        streams_list = []

        for i in yt.streams:
            if '1080p' in str(i) and '60fps' in str(i):
                streams_list.append(i)

        stream = streams_list[0]
        print("DownLoad :", stream)
        stream.download(DOWNLOAD_FOLDER, filename="original_download_video.mp4")
        
        cap = cv2.VideoCapture('./original_download_video.mp4')
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        writer = cv2.VideoWriter('./download_video.mp4', fourcc, 60, (int(width), int(height)))
        
        for i in range(60 * 180):
            _, frame = cap.read()
            writer.write(frame)
        
        cap.release()
        writer.release()
                    
        print("Done.")
    else:
        print("Already Exist Mp4")


with DAG( **dag_args ) as dag:
    depedency_check = PythonOperator(
        task_id='depedency_check',
        python_callable=depedency_check,
    )

    create_train_dataset = PythonOperator(
        task_id='create_train_dataset',
        python_callable=create_train_dataset,
    )

    get_video = PythonOperator(
        task_id='get_video',
        python_callable=youtube_download,
    )

    train_model = BashOperator(
        task_id='train_model',
        bash_command='src/train.sh',
    )

    detect_model = BashOperator(
        task_id='detect_model',
        bash_command='src/detect.sh',
    )

    depedency_check >> create_train_dataset >> get_video >> train_model >> detect_model
