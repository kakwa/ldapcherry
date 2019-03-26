FROM ubuntu:16.04

ADD . .
RUN apt update && apt install -y python3 python3-pip && pip3 install -e . -r requirements.txt && pip3 install pycodestyle passlib coveralls && /usr/bin/python3 setup.py
VOLUME /etc/ldapcherry
EXPOSE 80

CMD ["ldapcherryd", "-c", "/etc/ldapcherry/ldapcherry.ini"]
