FROM ubuntu:16.04

ADD . /opt/
WORKDIR "/opt"
RUN apt update && apt install -y python-dev python-pip libldap2-dev libsasl2-dev libssl-dev
RUN pip install -e /opt/ -r /opt/requirements.txt
RUN pip install pycodestyle passlib coveralls
RUN /usr/bin/python2 /opt/setup.py install

VOLUME /etc/ldapcherry
EXPOSE 80

CMD ["/usr/bin/python2", "/opt/init.py"]
