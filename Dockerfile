FROM ubuntu:16.04
ADD . /leeroy
WORKDIR /leeroy
RUN apt-get update -qq --fix-missing && apt-get -q -y dist-upgrade && apt-get -y install python-pip
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 80
ENTRYPOINT ["/leeroy/bin/entry"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]

