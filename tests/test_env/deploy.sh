#!/bin/sh

DEBIAN_FRONTEND=noninteractive apt-get install ldap-utils slapd -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"  -f -q -y
DEBIAN_FRONTEND=noninteractive apt-get install samba -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"  -f -q -y

rsync -a `dirname $0`/ /
cd `dirname $0`/../../
sudo sed -i "s%template_dir.*%template_dir = '`pwd`/resources/templates/'%" /etc/ldapcherry/ldapcherry.ini
sudo sed -i "s%tools.staticdir.dir.*%tools.staticdir.dir = '`pwd`/resources/static/'%" /etc/ldapcherry/ldapcherry.ini

chown -R openldap:openldap /etc/ldap/
rm /etc/ldap/slapd.d/cn\=config/*mdb*
/etc/init.d/slapd restart
ldapadd -c -H ldap://localhost:390  -x -D "cn=admin,dc=example,dc=org" -f /etc/ldap/content.ldif -w password
if grep -q '127.0.0.1' /etc/hosts
then
    sed -i "s/\(127.0.0.1.*\)/\1 ldap.ldapcherry.org ad.ldapcherry.org ldap.dnscherry.org/" /etc/hosts
else
    echo '127.0.0.1 ldap.ldapcherry.org ad.ldapcherry.org ldap.dnscherry.org' >> /etc/hosts
fi 
cat /etc/hosts


df -h

smbconffile=/etc/samba/smb.conf
domain=dc
realm=dc.ldapcherry.org
sambadns=SAMBA_INTERNAL
targetdir=/var/lib/samba/
role=dc
sambacmd=samba-tool
adpass=qwertyP455

echo "deploy AD"
printf '' > "${smbconffile}" && \
    ${sambacmd} domain provision ${hostip} \
    --domain="${domain}" --realm="${realm}" --dns-backend="${sambadns}" \
    --targetdir="${targetdir}" --use-rfc2307 \
    --configfile="${smbconffile}" --server-role="${role}" -d 1 --adminpass="${adpass}"
    

echo "Move configuration"
mv "${targetdir}/etc/smb.conf" "${smbconffile}"

mv /var/lib/samba/private/krb5.conf /etc/krb5.conf


sleep 5

#sh -x /etc/init.d/samba restart
/etc/init.d/samba-ad-dc restart
#sh -x /etc/init.d/smbd restart
#sh -x /etc/init.d/nmbd restart

sleep 5

netstat -apn
