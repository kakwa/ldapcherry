FROM ubuntu:16.04

ADD . /opt/
WORKDIR "/opt"
RUN apt update && apt install -y python-dev python-pip libldap2-dev libsasl2-dev libssl-dev && pip install -e /opt/ -r /opt/requirements.txt && pip install pycodestyle passlib coveralls && /usr/bin/python2 /opt/setup.py install
VOLUME /etc/ldapcherry
EXPOSE 80

CMD ["ldapcherryd", "-c", "/etc/ldapcherry/ldapcherry.ini"]
