# 使用基础的 Python 镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制应用程序代码到容器中
COPY . /app

# 安装依赖
RUN pip install paho-mqtt

# 执行应用程序
CMD ["python", "client.py"]
