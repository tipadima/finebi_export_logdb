FROM python:3.10.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV TZ="Asia/Yekaterinburg"

WORKDIR /opt/app
COPY requirements.txt /opt/app
COPY *.py /opt/app

RUN set -ex &&\
    addgroup --system --gid 1001 appuser &&\
    adduser --system -s /bin/false -u 1001 -g 1001 appuser &&\
    chown -R appuser:appuser /opt/app && \
    pip install --no-cache-dir -r /opt/app/requirements.txt

USER appuser
CMD ["python", "main.py"]

