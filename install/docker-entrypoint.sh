#!/bin/sh
set -eo pipefail

sed -i -r "s/ipaddress =.*/ipaddress=$HOST/" /opt/Yearning/src/deploy.conf
sed -i -r "s/address =.*/address=$MYSQL_ADDR/" /opt/Yearning/src/deploy.conf
sed -i -r "s/username =.*/username=$MYSQL_USER/" /opt/Yearning/src/deploy.conf
sed -i -r "s/password =.*/password=$MYSQL_PASSWORD/" /opt/Yearning/src/deploy.conf

touch /opt/Yearning/src/log/gunicorn.log
tail -n 0 -f /opt/Yearning/src/log/gunicorn.log &

exec "$@"
