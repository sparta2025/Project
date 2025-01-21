FROM python:3.8-slim

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc && \
    apt clean && rm -rf /var/lib/apt/lists/*

COPY ./req.txt /deploy/
COPY ./app.py /deploy/
COPY ./templates/index.html /deploy/templates/
COPY ./templates/static/css/styles.css /deploy/templates/static/css/
COPY ./templates/static/css/styles.css /deploy/static/css/
COPY ./ResNet-Conv2D.ver-16.2.4.qipc-562_errors-1.h5 /deploy/

WORKDIR /deploy/

RUN pip3 install --no-cache-dir -r req.txt

EXPOSE 5000

#ENV PORT 8010
#ENTRYPOINT ["python", "app.py"]

CMD ["python3", "app.py"]