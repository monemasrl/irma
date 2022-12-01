FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc g++ libc-dev linux-headers postgresql-dev cargo \
    && apk add libffi-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT [ "./docker-entrypoint.sh" ]
