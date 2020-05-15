FROM python:latest

ADD requirements.txt /config/requirements.txt
ADD *.py /workspace/
ADD rss_link.json /workspace/

WORKDIR /workspace

RUN apt-get update \
  && apt-get install -y busybox-static \
  && pip install --upgrade pip \
  && pip install -r /config/requirements.txt

ENV TZ=Asia/Tokyo
ENV RSS_LINK=/workspace/rss_link.json

COPY crontab /var/spool/cron/crontabs/root

CMD ["busybox", "crond", "-f", "-L", "/dev/stderr"]
