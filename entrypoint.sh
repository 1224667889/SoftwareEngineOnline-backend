#!/bin/bash
# $1: mysql_password
nginx

echo "$1"
service mysql start
mysql -uroot  -s -e "USE mysql;UPDATE user SET plugin='mysql_native_password' WHERE User='root';update mysql.user set authentication_string=password('$1') where user='root';update user set host = '%' where user = 'root';GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '$1' WITH GRANT OPTION;flush privileges;create database software charset=utf8;exit;"
service mysql restart

gunicorn start:app -c ./gunicorn.conf.py
