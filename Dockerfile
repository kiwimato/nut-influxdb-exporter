FROM python:alpine
MAINTAINER kiwimato <dub2sauce@gmail.com>

WORKDIR /src
COPY requirements.txt nut-influxdb-exporter.py run.sh /src/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/src/run.sh"]
