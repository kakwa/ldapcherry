FROM debian:stretch

ADD . /opt/
WORKDIR "/opt"
RUN apt update && \
    apt install -y python-dev python-pip libldap2-dev libsasl2-dev libssl-dev && \
    pip install -e /opt/ -r /opt/requirements-stretch.txt pycodestyle passlib coveralls configparser in_place && \
    /usr/bin/python2 /opt/setup.py install

VOLUME /etc/ldapcherry
EXPOSE 8080

CMD ["/usr/bin/python2", "/opt/init.py"]
