FROM python:3.8-slim

ENV KFSERVING_PORT 8081
ENV PROXY_PORT 5000
ENV ENVIRONMENT default

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT ["python"]

CMD ["app.py"]
