#!/bin/bash
# $1: local_mysql_password
# $2: remote_mysql_password
nginx

service mysql start
mysql -uroot  -s -e "USE mysql;UPDATE user SET plugin='mysql_native_password' WHERE User='root';update mysql.user set authentication_string=password('$1') where user='root';grant all privileges on *.* to 'root'@'%' identified by '$2' with grant option;flush privileges;create database software charset=utf8;exit;"
echo "bind-address=0.0.0.0" >> /etc/mysql/mysql.conf.d/mysqld.cnf
service mysql restart

gunicorn start:app -c ./gunicorn.conf.py
