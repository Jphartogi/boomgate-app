FROM ubuntu:20.04

USER root

ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV LIBGL_ALWAYS_INDIRECT=1

RUN apt-get update \
    && apt-get install -y \
    python3 python3-pyqt5 python3-pip

WORKDIR "/app"

RUN usermod -a -G audio root
RUN usermod -aG video root

COPY requirements.txt /app/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install wheel
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "./boomgate.py"]
