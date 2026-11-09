From python:3.15-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd app
USER app

CMD [ "python", "./launcher.py" ]
