FROM changchun/dvadmin3-base-backend-arm64:0.0.1
WORKDIR /backend
COPY ./backend/ .
RUN python3 -m pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
CMD ["sh","docker_start.sh"]
