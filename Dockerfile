FROM ubuntu:18.04
USER root

COPY sources.list /etc/apt/
RUN apt-get update -y \
	&& apt-get upgrade -y

RUN apt-get install "python3.7" -y \
    && apt-get install python3-pip -y \
    && apt-get install nginx -y \
    && apt-get install "mysql-server-5.7" -y \
    && apt-get install mongodb -y


COPY nginx.conf /etc/nginx/

WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY entrypoint.sh /app
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["mirror", "mirror"]
