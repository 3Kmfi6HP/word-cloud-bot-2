FROM node:latest

WORKDIR /app
RUN apt-get update && \
    npm install -g pm2 &&\
    apt-get install -y wget vim iproute2 coreutils systemd git psmisc bc sudo curl

# Install software-properties-common and add deadsnakes PPA
# RUN apt update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa

# Install python 3.7
RUN apt install python3.7 -y

# Set python 3.7 as the default python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --set python /usr/bin/python3.7

# Install python3-pip and upgrade pip
RUN apt install python3-pip -y
RUN python -m pip install --upgrade pip

RUN rm -rf /etc/localtime
# RUN curl -sL https://raw.githubusercontent.com/Unitech/pm2/master/packager/setup.deb.sh | sudo -E bash -
RUN ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    wget -O cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb &&\
    dpkg -i cloudflared.deb &&\
    rm -f cloudflared.deb
COPY . .
# COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x entrypoint.sh \
    && pip3 install -r requirements.txt
ENTRYPOINT ["sh", "/app/entrypoint.sh"]