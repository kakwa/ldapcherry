#!/bin/sh

apt update

DEBIAN_FRONTEND=noninteractive apt-get install ldap-utils slapd -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"  -f -q -y
DEBIAN_FRONTEND=noninteractive apt-get install samba-dsdb-modules samba-vfs-modules samba -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"  -f -q -y
DEBIAN_FRONTEND=noninteractive apt-get install winbind -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"  -f -q -y
DEBIAN_FRONTEND=noninteractive apt-get install build-essential python3-dev libsasl2-dev slapd ldap-utils tox lcov valgrind libtidy-dev libldap-dev python3-cherrypy python3-ldap python3-mako -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"  -f -q -y

[ -e '/etc/default/slapd' ] && rm -rf /etc/default/slapd
cp -r `dirname $0`/etc/default/slapd /etc/default/slapd
[ -e '/etc/ldap' ] && rm -rf /etc/ldap
cp -r `dirname $0`/etc/ldap /etc/ldap
[ -e '/etc/ldapcherry' ] && rm -rf /etc/ldapcherry
cp -r `dirname $0`/etc/ldapcherry /etc/ldapcherry

cd `dirname $0`/../../
sudo sed -i "s%template_dir.*%template_dir = '`pwd`/resources/templates/'%" /etc/ldapcherry/ldapcherry.ini
sudo sed -i "s%tools.staticdir.dir.*%tools.staticdir.dir = '`pwd`/resources/static/'%" /etc/ldapcherry/ldapcherry.ini

chown -R openldap:openldap /etc/ldap/
/etc/init.d/slapd restart
ldapadd -c -H ldap://localhost:390  -x -D "cn=admin,dc=example,dc=org" -f /etc/ldap/content.ldif -w password
if grep -q '127.0.0.1' /etc/hosts && ! grep -q 'ldap.ldapcherry.org' /etc/hosts
then
    sed -i "s/\(127.0.0.1.*\)/\1 ldap.ldapcherry.org ad.ldapcherry.org ldap.dnscherry.org/" /etc/hosts
else
    echo '127.0.0.1 ldap.ldapcherry.org ad.ldapcherry.org ldap.dnscherry.org' >> /etc/hosts
fi 
cat /etc/hosts


df -h

find /var/log/samba/ -type f -exec rm -f {} \;

smbconffile=/etc/samba/smb.conf
domain=dc
realm=dc.ldapcherry.org
sambadns=SAMBA_INTERNAL
targetdir=/var/lib/samba/
role=dc
sambacmd=samba-tool
adpass=qwertyP455

systemctl unmask samba-ad-dc

hostname ad.ldapcherry.org 
pkill -9 dnsmasq
pkill -9 samba

kill -9 `cat /var/run/samba/smbd.pid` 
rm -f /var/run/samba/smbd.pid
kill -9 `cat /var/run/samba/nmbd.pid` 
rm -f /var/run/samba/nmbd.pid
rm -rf /var/run/samba

echo "deploy AD"
printf '' > "${smbconffile}" && \
    ${sambacmd} domain provision ${hostip} \
    --domain="${domain}" --realm="${realm}" --dns-backend="${sambadns}" \
    --targetdir="${targetdir}" --use-rfc2307 \
    --configfile="${smbconffile}" --server-role="${role}" -d 1 --adminpass="${adpass}"
    

echo "Move configuration"
mv "${targetdir}/etc/smb.conf" "${smbconffile}"

cat ${smbconffile}

mv /var/lib/samba/private/krb5.conf /etc/krb5.conf

sleep 15

systemctl restart samba-ad-dc
/etc/init.d/samba-ad-dc restart

cat /var/log/samba/*

sleep 5

samba-tool domain passwordsettings set -d 1 --complexity off
samba-tool domain passwordsettings set -d 1 --min-pwd-length 0
systemctl status samba-ad-dc
ss -apn | grep samba
