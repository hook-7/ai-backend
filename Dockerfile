# 使用官方 Python 镜像作为基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app



COPY . .

RUN pip install -r requirements.txt

ENV HTTP_PROXY="http://10.10.10.10:30809"
ENV HTTPS_PROXY="http://10.10.10.10:30809"

# 暴露端口
EXPOSE 8000

# 启动命令
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
