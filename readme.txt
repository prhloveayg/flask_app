# 运行说明

本工程用docker-compose构建。

在运行docker-compose之前，一定要确定自己电脑的5000端口，3306端口和1883端口未被占用。

1. 将本工程放到一个英文路径下
2. cd path/to/project
3. sudo docker-compose up
4. 等待构建完成，打印出flask_app服务准备完成的信息后，可以访问网页
   1. 在本机上，打开浏览器输入`127.0.0.1:5000`
   2. 在其他电脑或手机端，打开浏览器输入`ip.of.your.computer:5000`（ip地址可以用`ifconfig` 或`ipconfig`查看）

注：本项目是在MacOS上开发和测试的

注：地图功能需要开代理，因为有一个底图是国外的。如果不搭梯子可能速度很慢或者加载不出来。

