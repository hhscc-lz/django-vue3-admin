FROM changchun/dvadmin3-base-web-arm64:0.0.1
WORKDIR /web/
COPY web/. .
RUN yarn install --registry=https://registry.npmmirror.com
RUN yarn build

FROM nginx:1.29.0
COPY ./docker_env/nginx/my.conf /etc/nginx/conf.d/my.conf
COPY --from=0 /web/dist /usr/share/nginx/html
