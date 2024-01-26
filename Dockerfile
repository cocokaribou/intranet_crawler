FROM python:3.10.12

WORKDIR /intranet_crawler

COPY . /intranet_crawler

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

ENV NAME World

CMD ["python3", "app.py"]
