FROM rackspacedot/python37:latest
RUN apt-get update -y
RUN apt-get install git -y
RUN apt-get install psmisc -y
RUN apt-get install bc -y
RUN rm -rf /etc/localtime
RUN ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
COPY . /root/word_cloud_bot
COPY entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh \
    && pip3 install -r /root/word_cloud_bot/requirements.txt
ENTRYPOINT ["sh", "/root/entrypoint.sh"]