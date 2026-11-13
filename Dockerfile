From python:3.15-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd app
RUN chown -R app /usr/src/app
USER app

CMD [ "python", "./launcher.py" ]
