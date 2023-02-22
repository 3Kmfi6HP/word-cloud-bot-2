import datetime
import time
import connector
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters
from config import TOKEN, LIMIT_COUNT, EXCLUSIVE_MODE, RANK_COMMAND_MODE, OWNER, EXCLUSIVE_LIST, CHANNEL, HELP
import schedule
from task import add_task, add_user_task

bot = telegram.Bot(token=TOKEN)


def start(update, context):
    # 限制不为群组
    chat_type = update.effective_chat.type
    if chat_type == "supergroup":
        return
    try:
        connector.get_connection().keys()
        print('进入 start 函数')
        update.message.reply_text(
            HELP,
            parse_mode='HTML'
        )
    except Exception as e:
        print(e)
        print('进入start函数')
        if update.effective_user.id == OWNER:
            update.message.reply_text(f"系统故障，Redis连接失败，错误信息：\n{e}")


def ping(update, context):
    # 限制不为群组
    chat_type = update.effective_chat.type
    if chat_type == "supergroup":
        return
    try:
        delay = connector.get_connection().ping()
        connector.get_connection().keys()
        print('进入 ping 函数')
        update.message.reply_text(
            'pong~'+str(delay),
        )
    except Exception as e:
        print(e)


def rank(update, context):
    try:
        r = connector.get_connection()
        chat_type = update.effective_chat.type
        user_id = update.effective_user.id
        chat_id = update.effective_message.chat_id
        try:
            username = update.effective_user.username
        except Exception as e:
            username = update.effective_user.id
        # 限制为群组
        if chat_type != "supergroup":
            update.message.reply_text("此命令只有在群组中有效！")
            return
        if RANK_COMMAND_MODE:
            try:
                chat_member = bot.get_chat_member(chat_id, user_id)
                status = chat_member["status"]
                if user_id == 461927973:
                    status = "administrator"
                print("此用户在群组中身份为： {}".format(status))
                if status == "creator" or status == "administrator":
                    print("用户权限正确")
                else:
                    return
            except Exception as e:
                print(e)
                print("获取用户身份失败")
        if r.exists("{}_frequency_limit".format(chat_id)):
            r.setrange("{}_frequency_limit".format(chat_id), 0, int(r.get("{}_frequency_limit".format(chat_id))) + 1)
        else:
            struct_time = time.localtime(time.time())
            # 数据过期时间为当前小时的 59 分
            ex_time = datetime.datetime(
                struct_time.tm_year,
                struct_time.tm_mon,
                struct_time.tm_mday,
                struct_time.tm_hour,
                59
            )
            r.set("{}_frequency_limit".format(chat_id), 1)
            r.expireat("{}_frequency_limit".format(chat_id), ex_time)
        count = int(r.get("{}_frequency_limit".format(chat_id)))
        if count > LIMIT_COUNT:
            update.message.reply_text("该群组在这个小时内的生成配额已经用完，请稍后再试~")
            return
        add_task(chat_id)
        print("群组: {}，用户: {}|{} 发起了主动触发请求".format(chat_id, username, user_id, ))
        if not CHANNEL == 0:
            ctext = f'#WORDCLOUD #APPLY \n' \
                    f'群组 ID：`{chat_id}`\n' \
                    f'用户 ID：`{user_id}`\n' \
                    f'执行操作：`主动生成词云`'
            bot.send_message(chat_id=CHANNEL, text=ctext, parse_mode="Markdown")
        update.message.reply_text("统计数据将在分析完毕后发送到当前群组，请稍等~")
    except Exception as e:
        print("主动触发任务失败，请检查")
        print(e)


def stat(update, context):
    try:
        r = connector.get_connection()
        chat_type = update.effective_chat.type
        user_id = update.effective_user.id
        chat_id = update.effective_message.chat_id
        try:
            username = update.effective_user.username
        except Exception as e:
            username = update.effective_user.id
        # 限制为群组
        if chat_type != "supergroup":
            update.message.reply_text("此命令只有在群组中有效！")
            return
        if r.exists("{}_{}_frequency_limit".format(chat_id, user_id)):
            r.setrange("{}_{}_frequency_limit".format(chat_id, user_id), 0,
                       int(r.get("{}_{}_frequency_limit".format(chat_id, user_id))) + 1)
        else:
            struct_time = time.localtime(time.time())
            # 数据过期时间为当前小时的 59 分
            ex_time = datetime.datetime(
                struct_time.tm_year,
                struct_time.tm_mon,
                struct_time.tm_mday,
                struct_time.tm_hour,
                59
            )
            r.set("{}_{}_frequency_limit".format(chat_id, user_id), 1)
            r.expireat("{}_{}_frequency_limit".format(chat_id, user_id), ex_time)
        count = int(r.get("{}_{}_frequency_limit".format(chat_id, user_id)))
        if count > LIMIT_COUNT:
            update.message.reply_text(f"[您](tg://user?id={user_id}):在这个小时内的生成配额已经用完，请稍后再试~")
            return
        add_user_task(chat_id, user_id)
        print("群组: {}，用户: {} | {} 发起了主动触发请求".format(chat_id, username, user_id, ))
        if not CHANNEL == 0:
            ctext = f'#WORDCLOUD #APPLY #id{user_id} \n' \
                    f'群组 ID：`{chat_id}`\n' \
                    f'用户 ID：`{user_id}`\n' \
                    f'执行操作：`主动生成用户词云`'
            bot.send_message(chat_id=CHANNEL, text=ctext, parse_mode="Markdown")
        update.message.reply_text("统计数据将在分析完毕后发送到当前群组，请稍等~")
    except Exception as e:
        print("主动触发任务失败，请检查")
        print(e)


def chat_content_exec(update, context):
    try:
        r = connector.get_connection()
        text = update.message.text
        chat_type = update.effective_chat.type
        user_id = update.effective_user.id
        chat_id = update.effective_message.chat_id
        # 限制为群组
        if chat_type != "supergroup":
            return
        # 限制文字长度不能超过80字
        if len(text) > 80:
            return
        # 独享模式（仅授权群组可用）
        if EXCLUSIVE_MODE and chat_id not in EXCLUSIVE_LIST:
            print(chat_id + " 为未认证群组，取消入库")
            return
        user = update.message.from_user
        firstname = str(user["first_name"])
        name = firstname
        print("\n---------------------------")
        print("内容: " + text[:10])
        print("群组类型: " + str(chat_type))
        print("用户ID: " + str(user_id))
        print("chat_id: " + str(chat_id))
        if text.startswith('/') or '//' in text or text.startswith('-'):
            print("这是一条指令或者链接信息，跳过")
            return
        else:
            if text[-1] not in ["，", "。", "！", "：", "？", "!", "?", ",", ":", "."]:
                r.append("{}_chat_content".format(chat_id), text + "。")
                r.append("{}_{}_user_content".format(chat_id, user_id), text + "。")
            else:
                r.append("{}_chat_content".format(chat_id), text)
                r.append("{}_{}_user_content".format(chat_id, user_id), text)
            r.incrby("{}_total_message_amount".format(chat_id))
            r.incrby("{}_{}_user_message_amount".format(chat_id, user_id))
            r.hincrby("{}_user_message_amount".format(chat_id), name)
        print("---------------------------")
    except Exception as e:
        print(e)
        print("用户数据提取、入库错误")


def check_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


start_handler = CommandHandler('start', start)
ping_handler = CommandHandler('ping', ping)
rank_handler = CommandHandler('rank', rank)
stat_handler = CommandHandler('stat', stat)
chat_content_handler = MessageHandler(Filters.text, chat_content_exec)
