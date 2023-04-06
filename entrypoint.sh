#! /bin/sh \
RELEASE_RANDOMNESS=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 16)
RELEASE_RANDOMNESS2=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 12)
RELEASE_RANDOMNESS3=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 10)
generate_argo() {
  cat > argo.sh << ABC
#!/usr/bin/env bash
argo_type() {
  if [[ -n "\${ARGO_AUTH}" && -n "\${ARGO_DOMAIN}" ]]; then
    [[ \$ARGO_AUTH =~ TunnelSecret ]] && echo \$ARGO_AUTH > tunnel.json && echo -e "tunnel: \$(cut -d\" -f12 <<< \$ARGO_AUTH)\ncredentials-file: /app/tunnel.json" > tunnel.yml
  else
    ARGO_DOMAIN=\$(cat argo.log | grep -o "info.*https://.*trycloudflare.com" | sed "s@.*https://@@g" | tail -n 1)
  fi
}
export_list() {
  VMESS="{ \"v\": \"2\", \"ps\": \"Argo-Vmess\", \"add\": \"icook.hk\", \"port\": \"443\", \"id\": \"${UUID}\", \"aid\": \"0\", \"scy\": \"none\", \"net\": \"ws\", \"type\": \"none\", \"host\": \"\${ARGO_DOMAIN}\", \"path\": \"/${WSPATH}-vmess?ed=2048\", \"tls\": \"tls\", \"sni\": \"\${ARGO_DOMAIN}\", \"alpn\": \"\" }"
}
argo_type
export_list
ABC
}

generate_nezha() {
  cat > nezha.sh << EOF
#!/usr/bin/env bash
# 检测是否已运行
check_run() {
  [[ \$(pgrep -laf ${RELEASE_RANDOMNESS}) ]] && echo "哪吒客户端正在运行中" && exit
}
# 三个变量不全则不安装哪吒客户端
check_variable() {
  [[ -z "\${NEZHA_SERVER}" || -z "\${NEZHA_PORT}" || -z "\${NEZHA_KEY}" ]] && exit
}
# 下载最新版本 Nezha Agent
download_agent() {
  if [ ! -e nezha-agent ]; then
    URL=\$(wget -qO- -4 "https://api.github.com/repos/naiba/nezha/releases/latest" | grep -o "https.*linux_amd64.zip")
    wget -t 2 -T 10 -N \${URL}
    unzip -qod ./ nezha-agent_linux_amd64.zip && rm -f nezha-agent_linux_amd64.zip
    mv /app/nezha-agent /app/${RELEASE_RANDOMNESS}
    chmod +x /app/${RELEASE_RANDOMNESS}
  fi
}
check_run
check_variable
download_agent
EOF
}

generate_pm2_file() {
  if [[ -n "${ARGO_AUTH}" && -n "${ARGO_DOMAIN}" ]]; then
    [[ $ARGO_AUTH =~ TunnelSecret ]] && ARGO_ARGS="tunnel --edge-ip-version auto --config tunnel.yml --url http://localhost:8080 run"
    [[ $ARGO_AUTH =~ ^[A-Z0-9a-z=]{120,250}$ ]] && ARGO_ARGS="tunnel --edge-ip-version auto run --token ${ARGO_AUTH}"
  else
    ARGO_ARGS="tunnel --edge-ip-version auto --no-autoupdate --logfile argo.log --loglevel info --url http://localhost:8080"
  fi

  if [[ -z "${NEZHA_SERVER}" || -z "${NEZHA_PORT}" || -z "${NEZHA_KEY}" ]]; then
    cat > ecosystem.config.js << EOF
  module.exports = {
  "apps":[
      {
          "name":"web",
          "script":"/app/web.js run"
      },
      {
          "name":"argo",
          "script":"cloudflared",
          "args":"${ARGO_ARGS}"
      }
  ]
}
EOF
  else
    cat > ecosystem.config.js << EOF
module.exports = {
  "apps": [
    {
      "name": "argo",
      "script": "cloudflared",
      "args": "${ARGO_ARGS}",
      "autorestart": true,
      "restart_delay": 5000
    },
    {
      "name": "nztz",
      "script": "/app/${RELEASE_RANDOMNESS}",
      "args": "-s ${NEZHA_SERVER}:${NEZHA_PORT} -p ${NEZHA_KEY}",
      "autorestart": true,
      "restart_delay": 5000
    }
  ],
   "max_memory_restart": "500M"
}
EOF
  fi
}

# generate_config
# generate_config_yml
# generate_ca
generate_argo
generate_nezha
generate_pm2_file
[ -e nezha.sh ] && bash nezha.sh
[ -e argo.sh ] && bash argo.sh
[ -e ecosystem.config.js ] && pm2 start
# cd /root/word_cloud_bot && python3 main.py >> output 2>&1 &
tail -f /dev/null