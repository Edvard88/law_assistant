FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

# Надо создавать еще виртуальное окружение
# sudo apt update
# sudo apt install libpango1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0

RUN pip install -r requirements.txt