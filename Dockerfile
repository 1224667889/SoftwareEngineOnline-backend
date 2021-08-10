FROM ubuntu:18.04
USER root

COPY sourses.list /etc/apt/
RUN apt-get update \
	&& apt-get upgrade

RUN apt-get install "python3.7" -y \
    && apt-get install python3-pip -y \
    && apt-get install nginx -y \
    && apt-get install "mysql-server-5.7" -y

#RUN service mysql start
#RUN mysql -uroot  -s -e "set password for root@localhost = password('mirror');exit"
#    && set password for root@localhost = password('mirror'); \
#    && exit

COPY nginx.conf /etc/nginx/
#RUN nginx

WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY entrypoint.sh /app
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["mirror"]
