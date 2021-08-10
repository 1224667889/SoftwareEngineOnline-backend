### 2021秋福州大学软工实践 - 后端部分

在项目目录下执行代码上传：

`scp -r ../SoftwareEngineOnline-backend hadoop@172.17.173.97:`

项目运行：

```shell
sudo su
cd SoftwareEngineOnline-backend

# 1.0是版本号，也可以写成latest 最后还有个"."别忘了
docker build -t software_engine:1.0 .

# 创建容器，执行脚本(entrypoint.sh)
# 端口号映射 后端端口：8080->8080 数据库端口：4036->3306
docker run -itd --name software_engine_container -p 8080:8080 -p 4036:3306 software_engine:1.0

# 运行日志
docker logs -f software_engine_container
```
