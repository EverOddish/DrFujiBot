FROM python:3

WORKDIR /app

COPY drfujibot_irc.py .
COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

CMD ["python", "drfujibot_irc.py"]
