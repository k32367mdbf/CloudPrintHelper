import os
import json
from io import BytesIO
from pprint import pprint
from flask import Flask, request as 請求
from telegram import(
    Bot,
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    File,
)
from telegram.ext import (
    Dispatcher,
    CommandHandler as 指令訊息,
    MessageHandler as 文字訊息,
    CallbackQueryHandler as 按鈕訊息,
    Filters,
)
import requests
from fsm import 狀態機
from config import *
from cloudPrint import ibon列印小幫手


伺服器 = Flask(__name__)
機器人 = Bot(token = TOKEN)
分配器 = Dispatcher(機器人, None, workers=0)
用戶狀態 = 狀態機()


# 取得ngrok網址並設定webhook
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':   # 防止debug模式下執行兩次
    回覆 = requests.get('http://localhost:4040/api/tunnels/command_line')
    WEBHOOK = json.loads(回覆.text)['public_url']
    機器人.setWebhook(WEBHOOK)
    print('WEBHOOK: '+WEBHOOK)


# 設定路由
@伺服器.route('/', methods=['POST'])
def 接收訊息():
    訊息 = Update.de_json(請求.get_json(force=True), 機器人)   # 解析訊息
    分配器.process_update(訊息)   # 丟給分配器
    # pprint(請求.get_json(force=True))
    return '收到！'


# 註冊處理訊息的修飾器
def 處理(handler,cmd=None,**kw):
    def decorater(func):
        def wrapper(*args,**kw):
            return func(*args,**kw)
        if cmd==None:
            func_hander=handler(func,**kw)
        else:
            func_hander=handler(cmd,func,**kw)
        分配器.add_handler(func_hander)
        return wrapper
    return decorater


# 處理各種訊息
@處理(指令訊息, 'start')
def start指令(機器人, 訊息):
    選單 = ReplyKeyboardMarkup([
        ['設定預設名稱', '設定預設信箱'],
        ['設定預設上傳超商'],
        ['設定每次詢問項目'],
        ['說明頁面', '目前設定值'],
        ])
    訊息.message.reply_text("哈囉～\n可以直接丟檔案給我\n或用下面選單喔", reply_markup=選單)
    # 訊息.message.reply_text("[inline](https://imgur.com/a/wBJmQ)", parse_mode=ParseMode.MARKDOWN)
    # 訊息.message.reply_photo(open('resource/uploading.gif', 'rb'))
    # update.message.chat_id
    # parse_mode=ParseMode.MARKDOWN
    # https://imgur.com/a/wBJmQ


@處理(文字訊息, Filters.document)
def 處理檔案(機器人, 訊息):
    用戶狀態.接收檔案(訊息)


# @處理(文字訊息, Filters.entity('url'))
# def 處理連結(機器人, 訊息):
#     用戶狀態.接收檔案(訊息)


@處理(文字訊息, Filters.entity('email'))
def 處理信箱(機器人, 訊息):
    if 用戶狀態.state == '輸入信箱':
        if 用戶狀態._狀態機__預設項目['詢問項目']['上傳超商']:
            用戶狀態.選擇上傳超商(訊息)
        else:
            用戶狀態.上傳檔案(訊息, 機器人=機器人)
    elif 用戶狀態.state == '設定預設信箱':
        用戶狀態.完成設定預設信箱(訊息, 驗證=True)
    elif 用戶狀態.state == '輸入名稱':
        if 用戶狀態._狀態機__預設項目['詢問項目']['信箱']:
            用戶狀態.輸入信箱(訊息)
        elif 用戶狀態._狀態機__預設項目['詢問項目']['上傳超商']:
            用戶狀態.選擇上傳超商(訊息)
        else:
            用戶狀態.上傳檔案(訊息, 機器人=機器人)
    elif 用戶狀態.state == '設定預設名稱':
        用戶狀態.完成設定預設名稱(訊息)
    else:
        訊息.message.reply_text('這裡不該輸入email')


@處理(文字訊息, Filters.text)
def 處理文字訊息(機器人, 訊息):
    if 用戶狀態.state == '初始狀態':
        if 訊息.message.text == '設定預設名稱':
            用戶狀態.設定預設名稱(訊息)

        elif 訊息.message.text == '設定預設信箱':
            用戶狀態.設定預設信箱(訊息)

        elif 訊息.message.text == '設定預設上傳超商':
            用戶狀態.設定預設上傳超商(訊息)

        elif 訊息.message.text == '設定每次詢問項目':
            用戶狀態.設定每次詢問項目(訊息)

        elif 訊息.message.text == '說明頁面':
            用戶狀態.說明頁面(訊息)

        elif 訊息.message.text == '目前設定值':
            用戶狀態.目前設定值(訊息)

        else:
            訊息.message.reply_text('可以用下面的選單喔～')

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    elif 用戶狀態.state == '接收檔案':
        訊息.message.reply_text('請傳ㄍ檔案給我')
    
    elif 用戶狀態.state == '輸入名稱':
        if 用戶狀態._狀態機__預設項目['詢問項目']['信箱']:
            用戶狀態.輸入信箱(訊息)
        elif 用戶狀態._狀態機__預設項目['詢問項目']['上傳超商']:
            用戶狀態.選擇上傳超商(訊息)
        else:
            用戶狀態.上傳檔案(訊息, 機器人=機器人)

    elif 用戶狀態.state == '輸入信箱':
        訊息.message.reply_text('信箱請符合格式')

    elif 用戶狀態.state == '選擇上傳超商':
        訊息.message.reply_text('請使用鍵盤選擇上傳超商～')

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    elif 用戶狀態.state == '設定預設名稱':
        用戶狀態.完成設定預設名稱(訊息)

    elif 用戶狀態.state == '設定預設信箱':
        用戶狀態.完成設定預設信箱(訊息, 驗證=False)

    elif 用戶狀態.state == '設定預設上傳超商':
        訊息.message.reply_text('請使用鍵盤設定預設上傳超商～') 

    elif 用戶狀態.state == '設定每次詢問項目':
        訊息.message.reply_text('請使用鍵盤設定每次詢問項目～')

    else:
        訊息.message.reply_text('怎麼可能RRRRRRRRRRRRRRR～')


@處理(按鈕訊息)
def 處理按鈕訊息(機器人, 訊息):
    if 用戶狀態.state == '接收檔案':
        if 訊息.callback_query.data == '上傳':
            if 用戶狀態._狀態機__預設項目['詢問項目']['名稱']:
                用戶狀態.輸入名稱(訊息)
            elif 用戶狀態._狀態機__預設項目['詢問項目']['信箱']:
                用戶狀態.輸入信箱(訊息)
            elif 用戶狀態._狀態機__預設項目['詢問項目']['上傳超商']:
                用戶狀態.選擇上傳超商(訊息)
            else:
                用戶狀態.上傳檔案(訊息, 機器人=機器人)
        elif 訊息.callback_query.data == '取消':
            用戶狀態.回初始狀態(訊息)
          
    elif 用戶狀態.state == '選擇上傳超商':
        if 訊息.callback_query.data == '7-11':
            用戶狀態._狀態機__暫存項目['上傳超商']['7-11'] ^= True
        elif 訊息.callback_query.data == '全家':
            用戶狀態._狀態機__暫存項目['上傳超商']['全家'] ^= True
        elif 訊息.callback_query.data == '萊爾富':
            用戶狀態._狀態機__暫存項目['上傳超商']['萊爾富'] ^= True
        elif 訊息.callback_query.data == '確定':
            用戶狀態.上傳檔案(訊息, 機器人=機器人)
            return
        elif 訊息.callback_query.data == '取消':
            用戶狀態.回初始狀態(訊息)
            return
        選單 = InlineKeyboardMarkup([[
            InlineKeyboardButton('7-11', callback_data='7-11'),
            InlineKeyboardButton('全家', callback_data='全家'),
            InlineKeyboardButton('萊爾富', callback_data='萊爾富')],[
            InlineKeyboardButton('確定', callback_data='確定'),
            InlineKeyboardButton('取消', callback_data='取消')
        ]])
        本文 = \
        "請選擇預設上傳超商\n"+\
        f"    {'✔' if 用戶狀態._狀態機__暫存項目['上傳超商']['7-11'] else '❌'} 7-11\n"+\
        f"    {'✔' if 用戶狀態._狀態機__暫存項目['上傳超商']['全家'] else '❌'} 全家\n"+\
        f"    {'✔' if 用戶狀態._狀態機__暫存項目['上傳超商']['萊爾富'] else '❌'} 萊爾富\n"
        訊息.callback_query.message.edit_text(本文, reply_markup=選單, parse_mode=ParseMode.MARKDOWN)
    
    elif 用戶狀態.state == '設定預設上傳超商':
        if 訊息.callback_query.data == '7-11':
            用戶狀態._狀態機__暫存項目['上傳超商']['7-11'] ^= True
        elif 訊息.callback_query.data == '全家':
            用戶狀態._狀態機__暫存項目['上傳超商']['全家'] ^= True
        elif 訊息.callback_query.data == '萊爾富':
            用戶狀態._狀態機__暫存項目['上傳超商']['萊爾富'] ^= True
        elif 訊息.callback_query.data == '確定':
            用戶狀態.完成設定預設上傳超商(訊息, 驗證=True)
            return
        elif 訊息.callback_query.data == '取消':
            用戶狀態.完成設定預設上傳超商(訊息, 驗證=False)
            return
        選單 = InlineKeyboardMarkup([[
            InlineKeyboardButton('7-11', callback_data='7-11'),
            InlineKeyboardButton('全家', callback_data='全家'),
            InlineKeyboardButton('萊爾富', callback_data='萊爾富')],[
            InlineKeyboardButton('確定', callback_data='確定'),
            InlineKeyboardButton('取消', callback_data='取消')
        ]])
        本文 = \
        "請選擇預設上傳超商\n"+\
        f"    {'✔' if 用戶狀態._狀態機__暫存項目['上傳超商']['7-11'] else '❌'} 7-11\n"+\
        f"    {'✔' if 用戶狀態._狀態機__暫存項目['上傳超商']['全家'] else '❌'} 全家\n"+\
        f"    {'✔' if 用戶狀態._狀態機__暫存項目['上傳超商']['萊爾富'] else '❌'} 萊爾富\n"
        訊息.callback_query.message.edit_text(本文, reply_markup=選單, parse_mode=ParseMode.MARKDOWN)
    
    elif 用戶狀態.state == '設定每次詢問項目':
        if 訊息.callback_query.data == '名稱':
            用戶狀態._狀態機__暫存項目['詢問項目']['名稱'] ^= True
        elif 訊息.callback_query.data == '信箱':
            用戶狀態._狀態機__暫存項目['詢問項目']['信箱'] ^= True
        elif 訊息.callback_query.data == '上傳超商':
            用戶狀態._狀態機__暫存項目['詢問項目']['上傳超商'] ^= True
        elif 訊息.callback_query.data == '確定':
            用戶狀態.完成設定每次詢問項目(訊息, 驗證=True)
            return
        elif 訊息.callback_query.data == '取消':
            用戶狀態.完成設定每次詢問項目(訊息, 驗證=False)
            return
        選單 = InlineKeyboardMarkup([[
            InlineKeyboardButton('名稱', callback_data='名稱'),
            InlineKeyboardButton('信箱', callback_data='信箱'),
            InlineKeyboardButton('上傳超商', callback_data='上傳超商'),],[
            InlineKeyboardButton('確定', callback_data='確定'),
            InlineKeyboardButton('取消', callback_data='取消')
        ]])
        本文 = \
        "請選擇每次詢問項目\n"+\
        f"    {'✔' if 用戶狀態._狀態機__暫存項目['詢問項目']['名稱'] else '❌'} 名稱\n"+\
        f"    {'✔' if 用戶狀態._狀態機__暫存項目['詢問項目']['信箱'] else '❌'} 信箱\n"+\
        f"    {'✔' if 用戶狀態._狀態機__暫存項目['詢問項目']['上傳超商'] else '❌'} 上傳超商\n"
        訊息.callback_query.message.edit_text(本文, reply_markup=選單, parse_mode=ParseMode.MARKDOWN)
    
    else:
        訊息.callback_query.message.reply_text('別亂按RRRRRRR～')

# 啟動伺服器
if __name__ == '__main__':
    伺服器.run(host = 'localhost', port = 2017, debug = True)

