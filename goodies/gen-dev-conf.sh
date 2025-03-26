#!/bin/sh

ROOT=$(readlink -f $(dirname $0)/../)

cp $ROOT/conf/ldapcherry.ini $ROOT/ldapcherry-dev.ini

sed -i "s|/etc/ldapcherry/|$ROOT/conf/|" $ROOT/ldapcherry-dev.ini
sed -i "s|/usr/share/ldapcherry/|$ROOT/resources/|" $ROOT/ldapcherry-dev.ini
sed -i "s|^ldap\.|#ldap.|" $ROOT/ldapcherry-dev.ini
sed -i "s|#demo\.|ldap.|" $ROOT/ldapcherry-dev.ini

GROUPS='cn=nagios admins\\,ou=Group\\,dc=example\\,dc=org, cn=users\\,ou=Group\\,dc=example\\,dc=org'
sed -i "s|ldap.admin.groups.*|ldap.admin.groups = '$GROUPS'|" $ROOT/ldapcherry-dev.ini


sed -i "s|^min_length.*|min_length = 3|" $ROOT/ldapcherry-dev.ini
sed -i "s|^min_upper.*|min_upper = 0|" $ROOT/ldapcherry-dev.ini
sed -i "s|^min_digit.*|min_digit = 0|" $ROOT/ldapcherry-dev.ini
sed -i "s|^min_punct.*|min_punct = 0|" $ROOT/ldapcherry-dev.ini
sed -i "s|^min_point.*|min_point = 0|" $ROOT/ldapcherry-dev.ini
