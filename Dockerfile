FROM locustio/locust

WORKDIR /locust

COPY ./ /locust

RUN pip install -r requirements.txt
