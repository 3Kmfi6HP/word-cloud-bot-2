FROM python:latest
WORKDIR /app
RUN apt-get update -y
RUN apt-get install wget -y
RUN apt-get install vim -y
RUN apt-get install -y iproute2 coreutils systemd
RUN apt-get install git -y
RUN apt-get install psmisc -y
RUN apt-get install bc -y
RUN rm -rf /etc/localtime
RUN apt install sudo curl && curl -sL https://raw.githubusercontent.com/Unitech/pm2/master/packager/setup.deb.sh | sudo -E bash -
RUN ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    wget -O cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb &&\
    dpkg -i cloudflared.deb &&\
    rm -f cloudflared.deb &&\
COPY . .
# COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x entrypoint.sh \
    && pip3 install -r requirements.txt
ENTRYPOINT ["sh", "entrypoint.sh"]