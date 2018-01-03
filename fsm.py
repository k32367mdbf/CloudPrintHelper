import os
import time
from io import BytesIO
from transitions import Machine
from telegram import(
    Bot, 
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
import requests
from cloudPrint import *


class 狀態機(Machine):

    __狀態 = [
        {'name': '初始狀態', 'on_enter': ['進入初始狀態']},
        {'name': '接收檔案', 'on_enter': ['進入接收檔案'], 'on_exit':['離開接收檔案']},
        {'name': '輸入名稱', 'on_enter': ['進入輸入名稱'], 'on_exit':['離開輸入名稱']},
        {'name': '輸入信箱', 'on_enter': ['進入輸入信箱'], 'on_exit':['離開輸入信箱']},
        {'name': '選擇上傳超商', 'on_enter': ['進入選擇上傳超商'], 'on_exit':['離開選擇上傳超商']},
        {'name': '上傳檔案', 'on_enter': ['進入上傳檔案'], 'on_exit':['離開上傳檔案']},
        {'name': '設定預設名稱', 'on_enter': ['進入設定預設名稱'], 'on_exit':['離開設定預設名稱']},
        {'name': '設定預設信箱', 'on_enter': ['進入設定預設信箱'], 'on_exit':['離開設定預設信箱']},
        {'name': '設定預設上傳超商', 'on_enter': ['進入設定預設上傳超商'], 'on_exit':['離開設定預設上傳超商']},
        {'name': '設定每次詢問項目', 'on_enter': ['進入設定每次詢問項目'], 'on_exit':['離開設定每次詢問項目']},
        {'name': '說明頁面', 'on_enter': ['進入說明頁面']},
        {'name': '目前設定值', 'on_enter': ['進入目前設定值']},
    ]

    __轉移函數 = [
        {
            'trigger': '接收檔案',
            'source': ['初始狀態', '接收檔案'],
            'dest': '接收檔案',
            'conditions': '檢查接收檔案'
        },
        {
            'trigger': '輸入名稱',
            'source': '接收檔案',
            'dest': '輸入名稱',
        },
        {
            'trigger': '輸入信箱',
            'source': ['接收檔案', '輸入名稱'],
            'dest': '輸入信箱',
        },
        {
            'trigger': '選擇上傳超商',
            'source': ['接收檔案', '輸入名稱', '輸入信箱'],
            'dest': '選擇上傳超商',
        },
        {
            'trigger': '上傳檔案',
            'source': ['接收檔案', '輸入名稱', '輸入信箱', '選擇上傳超商'],
            'dest': '上傳檔案',
        },
        # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        {
            'trigger': '設定預設名稱',
            'source': '初始狀態',
            'dest': '設定預設名稱',
        },
        {
            'trigger': '完成設定預設名稱',
            'source': '設定預設名稱',
            'dest': '初始狀態',
            'conditions': '檢查設定預設名稱',
        },
        # =======================================================
        {
            'trigger': '設定預設信箱',
            'source': '初始狀態',
            'dest': '設定預設信箱',
        },
        {
            'trigger': '完成設定預設信箱',
            'source': '設定預設信箱',
            'dest': '初始狀態',
            'conditions': '檢查設定預設信箱'
        },
        # =======================================================
        {
            'trigger': '設定預設上傳超商',
            'source': '初始狀態',
            'dest': '設定預設上傳超商',
        },
        {
            'trigger': '完成設定預設上傳超商',
            'source': '設定預設上傳超商',
            'dest': '初始狀態',
        },
        # =======================================================
        {
            'trigger': '設定每次詢問項目',
            'source': '初始狀態',
            'dest': '設定每次詢問項目',
        },
        {
            'trigger': '完成設定每次詢問項目',
            'source': '設定每次詢問項目',
            'dest': '初始狀態',
        },
        # =======================================================
        {
            'trigger': '說明頁面',
            'source': '初始狀態',
            'dest': '說明頁面',
        },
        {
            'trigger': '目前設定值',
            'source': '初始狀態',
            'dest': '目前設定值',
        },
        {
            'trigger': '回初始狀態',
            'source': ['接收檔案', '選擇上傳超商', '設定預設上傳超商', '上傳檔案', '說明頁面', '目前設定值'],
            'dest': '初始狀態',
        },
    ]

    def __init__(self):
        self.machine = Machine(
            model = self,
            states=self.__狀態,
            transitions=self.__轉移函數,
            initial='初始狀態')
        self.__ibon = ibon列印小幫手()
        # self.FamiPort = FamiPort列印小幫手()
        # self.萊爾富 = 萊爾富列印小幫手()
        self.__預設項目 = {
            '名稱': '雲端列印小幫手',
            '信箱': 'helper@cloudprint.com',
            '上傳超商': {
                '7-11': True,
                '全家': True,
                '萊爾富': False
            },
            '詢問項目': {
                '名稱': False,
                '信箱': False,
                '上傳超商': True
            },
        }
        self.__暫存項目 = {
            '名稱': self.__預設項目['名稱'],
            '信箱': self.__預設項目['信箱'],
            '上傳超商': {
                '7-11': True,
                '全家': True,
                '萊爾富': False
            },
            '詢問項目': {
                '名稱': False,
                '信箱': False,
                '上傳超商': True
            },
        }
        self.__檔案資訊 = []
        self.__欲傳檔案 = []

    # =======================================================
    def 進入初始狀態(self, 訊息, **其他參數):
        self.__檔案資訊 = []
        self.__欲傳檔案 = []
        self.__暫存項目['詢問項目']['名稱'] = self.__預設項目['詢問項目']['名稱']
        self.__暫存項目['詢問項目']['信箱'] = self.__預設項目['詢問項目']['信箱']
        if 訊息.callback_query:
            訊息.callback_query.message.reply_text("哈囉～\n可以直接丟檔案給我\n或用下面選單喔")
        else:
            訊息.message.reply_text("哈囉～\n可以直接丟檔案給我\n或用下面選單喔")

    # =======================================================   
    def 進入接收檔案(self, 訊息, **其他參數):
        pass

    def 檢查接收檔案(self, 訊息, **其他參數):
        檔名 = 訊息.message.document.file_name
        if os.path.splitext(檔名)[1][1:] not in \
        ('doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'txt', 'pdf'):
            訊息.message.reply_text('不支援RRRRRRRR！！')
            return False
        else:
            self.__檔案資訊.append({'檔名': 檔名, 'id': 訊息.message.document.file_id})
            選單 = InlineKeyboardMarkup([[
                InlineKeyboardButton('上傳', callback_data='上傳'),
                InlineKeyboardButton('取消', callback_data='取消')
            ]])
            本文 = ''
            for 檔案資訊 in self.__檔案資訊:
                本文 += (檔案資訊['檔名']+"\n")
            訊息.message.reply_text(本文, reply_markup=選單)
            return True

    def 離開接收檔案(self, 訊息, **其他參數):
        pass
    
    # =======================================================
    def 進入輸入名稱(self, 訊息, **其他參數):
        if 訊息.callback_query:
            訊息.callback_query.message.reply_text('請輸入名稱')
        else:
            訊息.message.reply_text('請輸入名稱')

    def 離開輸入名稱(self, 訊息, **其他參數):
        self.__暫存項目['名稱'] = 訊息.message.text

    # =======================================================
    def 進入輸入信箱(self, 訊息, **其他參數):
        if 訊息.callback_query:
            訊息.callback_query.message.reply_text('請輸入信箱')
        else:
            訊息.message.reply_text('請輸入信箱')

    def 離開輸入信箱(self, 訊息, **其他參數):
        self.__暫存項目['信箱'] = 訊息.message.text

    # =======================================================
    def 進入選擇上傳超商(self, 訊息, **其他參數):
        選單 = InlineKeyboardMarkup([[
            InlineKeyboardButton('7-11', callback_data='7-11'),
            InlineKeyboardButton('全家', callback_data='全家'),
            InlineKeyboardButton('萊爾富', callback_data='萊爾富')],[
            InlineKeyboardButton('確定', callback_data='確定'),
            InlineKeyboardButton('取消', callback_data='取消')
        ]])
        本文 = \
        "請選擇上傳超商\n"+\
        f"    {'✔' if self.__預設項目['上傳超商']['7-11'] else '❌'} 7-11\n"+\
        f"    {'✔' if self.__預設項目['上傳超商']['全家'] else '❌'} 全家\n"+\
        f"    {'✔' if self.__預設項目['上傳超商']['萊爾富'] else '❌'} 萊爾富\n"
        if 訊息.callback_query:
            訊息.callback_query.message.reply_text(本文, reply_markup=選單, parse_mode=ParseMode.MARKDOWN)
        else:
            訊息.message.reply_text(本文, reply_markup=選單, parse_mode=ParseMode.MARKDOWN)
    
    def 離開選擇上傳超商(self, 訊息, **其他參數):
        pass
    
    # =======================================================
    def 進入上傳檔案(self, 訊息, **其他參數):
        if 訊息.callback_query:
            訊息.callback_query.message.reply_text('準備中，請稍候...')
        else:
            訊息.message.reply_text('準備中，請稍候...')
        for 檔案資訊 in self.__檔案資訊:
            資訊 = 其他參數['機器人'].getFile(檔案資訊['id'])
            檔案 = BytesIO(requests.get(資訊.file_path).content)
            self.__欲傳檔案.append((檔案資訊['檔名'], 檔案.getvalue()))
        if 訊息.callback_query:
            訊息.callback_query.message.reply_text('上傳中，請稍候...')
        else:
            訊息.message.reply_text('上傳中，請稍候...')
        結果包 = self.__ibon.上傳(self.__欲傳檔案)
        本文 = ''
        for 結果 in 結果包:
            QRCode = BytesIO(結果['QRCode'])
            本文 = ('取件代碼： '+結果['取件代碼']+"\n列印期限： "+結果['列印期限']+"\n")
            if 訊息.callback_query:
                訊息.callback_query.message.reply_photo(QRCode)
                訊息.callback_query.message.reply_text(本文)
            else:
                訊息.message.reply_photo(QRCode)
                訊息.message.reply_text(本文)
        self.回初始狀態(訊息)

    def 離開上傳檔案(self, 訊息, **其他參數):
        pass

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    def 進入設定預設名稱(self, 訊息, **其他參數):
        訊息.message.reply_text('請輸入預設名稱')

    def 檢查設定預設名稱(self, 訊息, **其他參數):
        self.__預設項目['名稱'] = 訊息.message.text
        return True

    def 離開設定預設名稱(self, 訊息, **其他參數):
        訊息.message.reply_text('已設定好預設名稱')

    # =======================================================
    def 進入設定預設信箱(self, 訊息, **其他參數):
        訊息.message.reply_text('請輸入預設信箱')

    def 檢查設定預設信箱(self, 訊息, **其他參數):
        if 其他參數['驗證']:
            self.__預設項目['信箱'] = 訊息.message.text
            return True
        else:
            訊息.message.reply_text('預設信箱請符合格式')
            return False

    def 離開設定預設信箱(self, 訊息, **其他參數):
        訊息.message.reply_text('已設定好預設信箱')

    # =======================================================
    def 進入設定預設上傳超商(self, 訊息, **其他參數):
        選單 = InlineKeyboardMarkup([[
            InlineKeyboardButton('7-11', callback_data='7-11'),
            InlineKeyboardButton('全家', callback_data='全家'),
            InlineKeyboardButton('萊爾富', callback_data='萊爾富')],[
            InlineKeyboardButton('確定', callback_data='確定'),
            InlineKeyboardButton('取消', callback_data='取消')
        ]])
        本文 = \
        "請選擇預設上傳超商\n"+\
        f"    {'✔' if self.__預設項目['上傳超商']['7-11'] else '❌'} 7-11\n"+\
        f"    {'✔' if self.__預設項目['上傳超商']['全家'] else '❌'} 全家\n"+\
        f"    {'✔' if self.__預設項目['上傳超商']['萊爾富'] else '❌'} 萊爾富\n"
        訊息.message.reply_text(本文, reply_markup=選單, parse_mode=ParseMode.MARKDOWN)

    def 離開設定預設上傳超商(self, 訊息, **其他參數):
        if 其他參數['驗證']:
            self.__預設項目['上傳超商']['7-11'] = self.__暫存項目['上傳超商']['7-11']
            self.__預設項目['上傳超商']['全家'] = self.__暫存項目['上傳超商']['全家']
            self.__預設項目['上傳超商']['萊爾富'] = self.__暫存項目['上傳超商']['萊爾富']
            訊息.callback_query.message.edit_text('已完成設定預設上傳超商')
        else:
            self.__暫存項目['上傳超商']['7-11'] = self.__預設項目['上傳超商']['7-11']
            self.__暫存項目['上傳超商']['全家'] = self.__預設項目['上傳超商']['全家']
            self.__暫存項目['上傳超商']['萊爾富'] = self.__預設項目['上傳超商']['萊爾富']
            訊息.callback_query.message.edit_text('已取消設定預設上傳超商')

    # =======================================================
    def 進入設定每次詢問項目(self, 訊息, **其他參數):
        選單 = InlineKeyboardMarkup([[
            InlineKeyboardButton('名稱', callback_data='名稱'),
            InlineKeyboardButton('信箱', callback_data='信箱'),
            InlineKeyboardButton('上傳超商', callback_data='上傳超商'),],[
            InlineKeyboardButton('確定', callback_data='確定'),
            InlineKeyboardButton('取消', callback_data='取消')
        ]])
        本文 = \
        "請選擇每次詢問項目\n"+\
        f"    {'✔' if self.__預設項目['詢問項目']['名稱'] else '❌'} 名稱\n"+\
        f"    {'✔' if self.__預設項目['詢問項目']['信箱'] else '❌'} 信箱\n"+\
        f"    {'✔' if self.__預設項目['詢問項目']['上傳超商'] else '❌'} 上傳超商\n"
        訊息.message.reply_text(本文, reply_markup=選單, parse_mode=ParseMode.MARKDOWN)

    def 離開設定每次詢問項目(self, 訊息, **其他參數):
        if 其他參數['驗證']:
            self.__預設項目['詢問項目']['名稱'] = self.__暫存項目['詢問項目']['名稱']
            self.__預設項目['詢問項目']['信箱'] = self.__暫存項目['詢問項目']['信箱']
            self.__預設項目['詢問項目']['上傳超商'] = self.__暫存項目['詢問項目']['上傳超商']
            訊息.callback_query.message.edit_text('已完成設定每次詢問項目')
        else:
            self.__暫存項目['詢問項目']['名稱'] = self.__預設項目['詢問項目']['名稱']
            self.__暫存項目['詢問項目']['信箱'] = self.__預設項目['詢問項目']['信箱']
            self.__暫存項目['詢問項目']['上傳超商'] = self.__預設項目['詢問項目']['上傳超商']
            訊息.callback_query.message.edit_text('已取消設定每次詢問項目')

    # =======================================================
    def 進入說明頁面(self, 訊息, **其他參數):
        本文 = \
        "幫你傳要印的檔案到超商\n"+\
        "按下面的選單～～"
        訊息.message.reply_text(本文, parse_mode=ParseMode.MARKDOWN)
        self.回初始狀態()

    def 進入目前設定值(self, 訊息, **其他參數):
        本文 = \
        "🔰🔰目前設定值🔰🔰\n"+\
        f"名稱：{self.__預設項目['名稱']}\n"+\
        f"信箱：{self.__預設項目['信箱']}\n"+\
        "上傳超商：\n"+\
        f"    {'✔' if self.__預設項目['上傳超商']['7-11'] else '❌'} 7-11\n"+\
        f"    {'✔' if self.__預設項目['上傳超商']['全家'] else '❌'} 全家\n"+\
        f"    {'✔' if self.__預設項目['上傳超商']['萊爾富'] else '❌'} 萊爾富\n"+\
        "詢問項目：\n"+\
        f"    {'✔' if self.__預設項目['詢問項目']['名稱'] else '❌'} 名稱\n"+\
        f"    {'✔' if self.__預設項目['詢問項目']['信箱'] else '❌'} 信箱\n"+\
        f"    {'✔' if self.__預設項目['詢問項目']['上傳超商'] else '❌'} 上傳超商"
        訊息.message.reply_text(本文, parse_mode=ParseMode.MARKDOWN)
        self.回初始狀態()


# digraph finite_state_machine {
# 	rankdir=LR;
# 	node [shape = doublecircle]; 初始狀態;
# 	node [shape = circle];
#     初始狀態 -> 接收檔案 [ label = "接收檔案" ];
#     接收檔案 -> 接收檔案 [ label = "接收檔案" ];
    
#     接收檔案 -> 輸入名稱 [ label = "輸入名稱" ];
    
#     接收檔案 -> 輸入信箱 [ label = "輸入信箱" ];
#     輸入名稱 -> 輸入信箱 [ label = "輸入信箱" ];
    
#     接收檔案 -> 選擇上傳超商 [ label = "選擇上傳超商" ];
#     輸入名稱 -> 選擇上傳超商 [ label = "選擇上傳超商" ];
#     輸入信箱 -> 選擇上傳超商 [ label = "選擇上傳超商" ];
    
#     接收檔案 -> 上傳檔案 [ label = "上傳檔案" ];
#     輸入名稱 -> 上傳檔案 [ label = "上傳檔案" ];
#     輸入信箱 -> 上傳檔案 [ label = "上傳檔案" ];
#     選擇上傳超商 -> 上傳檔案 [ label = "上傳檔案" ];
#     上傳檔案 -> 初始狀態 [ label = "完成上傳檔案" ];
    	
#     初始狀態 -> 設定預設名稱 [ label = "設定預設名稱" ];
#     設定預設名稱 -> 初始狀態 [ label = "完成設定預設名稱" ];
#     初始狀態 -> 設定預設信箱 [ label = "設定預設信箱" ];
#     設定預設信箱 -> 初始狀態 [ label = "完成設定預設信箱" ];
#     初始狀態 -> 設定預設上傳超商 [ label = "設定預設上傳超商" ];
#     設定預設上傳超商 -> 初始狀態 [ label = "完成設定預設上傳超商" ];
#     初始狀態 -> 設定每次詢問項目 [ label = "設定每次詢問項目" ];
#     設定每次詢問項目 -> 初始狀態 [ label = "完成設定每次詢問項目" ];
#     初始狀態 -> 說明頁面 [ label = "說明頁面" ];
#     說明頁面 -> 初始狀態 [ label = "回初始狀態" ];
#     初始狀態 -> 目前設定值 [ label = "目前設定值" ];
#     目前設定值 -> 初始狀態 [ label = "回初始狀態" ];
# }