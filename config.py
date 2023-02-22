import os
TOKEN = os.environ['BOT_TOKEN'] # 你的机器人 token

# 频率限制次数，每个群每小时内，只能主动触发2次任务
LIMIT_COUNT = 2

# 私有模式，仅授权群组可用  False:关闭    True:打开
EXCLUSIVE_MODE = False

# 配置私有模式群组id列表（不私有请忽略） 例如：[-1001324252532, -100112415423]
EXCLUSIVE_LIST = []

# 跳过定时词云的群组
SKIP_SCHEDULE_GROUP = []

# 主动触发命令仅管理员有效  False:否     True:是
RANK_COMMAND_MODE = True

# 中文字体路径
FRONT = 'fonts/ZhuZiAWan-2.ttc'

# # Redis 配置
# 读取 env 中的 Redis 配置
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
REDIS_DB = int(os.getenv('REDIS_DB'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

REDIS_CONFIG = { 
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_DB,
    'password': REDIS_PASSWORD
}

# 拥有者 id 配置
OWNER = os.environ['OWNER_ID']

# 日志频道 id 0 为不启用
CHANNEL = os.environ['LOGS_CHANNEL']

# 帮助信息
HELP = '<b>Group Word Cloud Bot</b>\n\n/start - 查看此帮助信息\n/ping - 我还活着吗？\n/rank - 手动生成词云（绒布球）\n' \
       '/stat - 生成单用户词云\n\n' \
       '此项目开源于：https://git.io/JnrvH'
