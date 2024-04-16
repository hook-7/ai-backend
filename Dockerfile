# 使用官方 Python 镜像作为基础镜像
FROM python:latest

# 设置工作目录
WORKDIR /app


ENV HTTP_PROXY="http://10.10.10.10:30809"
ENV HTTPS_PROXY="http://10.10.10.10:30809"

# 将依赖复制到容器中
COPY requirements.txt .

# 安装依赖
RUN pip install -r requirements.txt

# 将应用代码复制到容器中
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
