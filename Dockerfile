FROM python:bullseye
WORKDIR /app
RUN apt-get update && \
    apt-get install -y wget vim iproute2 coreutils systemd git psmisc bc sudo curl
RUN rm -rf /etc/localtime
RUN curl -sL https://raw.githubusercontent.com/Unitech/pm2/master/packager/setup.deb.sh | sudo -E bash -
RUN ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    wget -O cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb &&\
    dpkg -i cloudflared.deb &&\
    rm -f cloudflared.deb
COPY . .
# COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x entrypoint.sh \
    && pip3 install -r requirements.txt
ENTRYPOINT ["sh", "/app/entrypoint.sh"]