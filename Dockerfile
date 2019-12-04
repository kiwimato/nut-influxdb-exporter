FROM python:alpine
MAINTAINER kiwimato <dub2sauce@gmail.com>

WORKDIR /src
COPY requirements.txt nut-influxdb-exporter.py /src/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash", "sleep.bash"]
