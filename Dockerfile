FROM ubuntu

RUN python setup.py
VOLUME /etc/ldapcherry
EXPOSE 80

CMD ["ldapcherryd", "-c", "/etc/ldapcherry/ldapcherry.ini"]
