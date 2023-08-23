FROM python:3.9-slim-buster

#ARG CONTEXT_NAME=training

RUN pip install --upgrade pip

#COPY ${CONTEXT_NAME}/requirements.txt /opt/ml/requirements.txt
COPY requirements.txt /opt/ml/requirements.txt

RUN pip3 install --upgrade -r /opt/ml/requirements.txt

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV AWS_BATCH_JOB_ID=default

COPY utils /opt/ml/utils
#COPY ${CONTEXT_NAME}/${CONTEXT_NAME}.py /opt/ml/${CONTEXT_NAME}.py
COPY training.py /opt/ml/training.py


ENTRYPOINT ["python3","/opt/ml/training.py"]
