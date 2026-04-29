FROM jrottenberg/ffmpeg:4.4-alpine

RUN apk add --no-cache python3 py3-pip
RUN pip3 install flask requests

WORKDIR /app
COPY . .

EXPOSE 5000

CMD ["python3", "app.py"]
