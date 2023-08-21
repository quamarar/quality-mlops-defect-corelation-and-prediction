FROM python:3.9-slim-buster

ARG CONTEXT_NAME=preprocessing

RUN pip install --upgrade pip

COPY ${CONTEXT_NAME}/requirements.txt /opt/ml/requirements.txt
RUN pip3 install --upgrade -r /opt/ml/requirements.txt

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV AWS_BATCH_JOB_ID=default

COPY utils /opt/ml/utils
COPY ${CONTEXT_NAME}/${CONTEXT_NAME}.py /opt/ml/${CONTEXT_NAME}.py

RUN ls -ltr /opt/ml/
RUN ls -ltr /opt/ml/utils

ENTRYPOINT ["python3","/opt/ml/preprocessing.py"]

# Build docker file from model folder to get full context so that it can copy utils folder as well

# cd model
# docker build -f preprocessing/Dockerfile . -t msil-preprocessing
# docker tag msil-preprocessing:latest 731580992380.dkr.ecr.ap-south-1.amazonaws.com/msil-preprocessing:latest
# docker run 731580992380.dkr.ecr.ap-south-1.amazonaws.com/msil-preprocessing:latest -h
# docker push 731580992380.dkr.ecr.ap-south-1.amazonaws.com/msil-preprocessing:latest
