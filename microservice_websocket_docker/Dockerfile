FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev \
    && apk add libffi-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "app.py" ]
