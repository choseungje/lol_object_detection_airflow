FROM apache/airflow:2.3.2
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim libgl1-mesa-glx libglib2.0-0 \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt requirements.txt
COPY ./yolov5 ./yolov5

# 권한이 없어 train.py or detect.py 실행 시 결과 저장을 위한 폴더를 생성하지 못함
# yolov5 folder의 소유권은 root가 가지고, airflow 유저는 root group에 포함됨
# root group의 유저들에게 yolov5의 쓰기 권한 부여
RUN chmod -R 775 ./yolov5

USER airflow
RUN pip install -r requirements.txt

