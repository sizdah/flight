import logging
import requests ,re
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
from telegram import Bot,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters
from time import sleep



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = '590253293:AAHxmKhXGS-o-MFjELhcU_bQ3rbhVc4Hqy8'
SITUATION= False
VALUE = 0
LINK = ""
GETSCAN = False
GETVALUE = False
def start(bot, update):
    update.message.reply_text('با زدن عبارت scan/ میتونید ناظر پرواز را ثبت کنید')
    update.message.reply_text('با زدن عبارت stop/ میتونید همیشه ناظر را غیرفعال کنید')

    bot = Bot(TOKEN)
    id = update.message.from_user.id
    id = int(id)

    custom_keyboard = [
        ['/scan'],
        ['/stop']
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=id, text="انتخاب کنید", reply_markup=reply_markup)



def engine(bot, update):
    global LINK
    global VALUE
    global SITUATION

    ###########



    while SITUATION:

        try:
            r = requests.get(LINK)
            c = r.content

            soup = BeautifulSoup(c, "html.parser")

            usd = soup.find_all("span", {"class": "price"})

            list = []

            for item in usd:
                mat = re.search(r'\d{3},\d{3}', str(item))
                mat = mat.group(0)
                mat = mat.replace(",", "")
                list.append(mat)

            list.sort()
            print(list[0])
            if int(list[0]) <= VALUE:
                price_found = str (list[0])
                goodnews = " یافت شد "+price_found
                update.message.reply_text(goodnews)
                update.message.reply_text(LINK)
                stop(bot,update)
                break

            updater1 = Updater(TOKEN)
            bot1 = updater1.bot
            dp1 = updater1.dispatcher
            dp1.add_handler(CommandHandler("stop", stop))
            updater1.start_polling()



        except:
            stop(bot,update)

        sleep(60)


def scan(bot, update):
 global GETSCAN
 GETSCAN=True
 update.message.reply_text('پرواز مورد نظر خود را ابتدار در سایت ghasedak24.com جستجو کنید و پس از جستجو لینک بالای مرورگر خود را بفرستید')
 update.message.reply_text('منتظر لینک....', reply_markup=ReplyKeyboardRemove())

def stop(bot, update):
 global SITUATION
 SITUATION=False
 global GETVALUE
 GETVALUE = False
 global GETSCAN
 GETSCAN = False
 update.message.reply_text('ناظر غیر فعال', reply_markup=ReplyKeyboardRemove())
 setup()



def echo(bot, update):
    global GETSCAN
    global LINK
    global GETVALUE
    global VALUE
    global SITUATION
    if GETSCAN:
        LINK = str(update.message.text)
        update.message.reply_text("حداقل مبلغ را به ریال وارد کنید")
        GETSCAN = False
        GETVALUE = True
    else:
        if GETVALUE:
            GETVALUE = False
            SITUATION = True
            VALUE = int(update.message.text)
            update.message.reply_text("ناظر اجرا شد")
            engine(bot,update)
        else:
            update.message.reply_text("از راهنما کمک بگیرید")
            update.message.reply_text("/start")


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

# Write your handlers here


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    if webhook_url:
        bot = Bot(TOKEN)
        update_queue = Queue()
        dp = Dispatcher(bot, update_queue)
    else:
        updater = Updater(TOKEN)
        bot = updater.bot
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("scan", scan))
        dp.add_handler(CommandHandler("stop", stop))
        dp.add_handler(CommandHandler("help", start))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, echo))

        # log all errors
        dp.add_error_handler(error)
    # Add your handlers here
    if webhook_url:
        bot.set_webhook(webhook_url=webhook_url)
        thread = Thread(target=dp.start, name='dispatcher')
        thread.start()
        return update_queue, bot
    else:
        bot.set_webhook()  # Delete webhook
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    setup()