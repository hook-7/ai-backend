# 使用官方 Python 镜像作为基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 将依赖复制到容器中
COPY . .

RUN pip install -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动命令
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
