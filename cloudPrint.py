import requests
from lxml import etree

class ibon列印小幫手(object):
    
    預設名稱 = '雲端列印小幫手'
    預設信箱 = 'helper@cloudprint.com'
    ibon網域 = 'http://www.ibon.com.tw/'
    填表頁面 = 'printscan_ie_innerifrm.aspx'
    查詢頁面 = 'printscan_fileupload_infor.aspx'
    __viewState = '/wEPDwUKMTk5Nzg0NzkyNg9kFgQCAQ8WAh4JaW5uZXJodG1sBRRpYm9uIOS+v+WIqeeUn+a0u+ermWQCAw8WAh4HZW5jdHlwZQUTbXVsdGlwYXJ0L2Zvcm0tZGF0YRYEAgkPDxYCHgRUZXh0BQIxMGRkAgsPDxYCHwIFVeaUr+aPtE1pY3Jvc29mdCBPZmZpY2Xns7vliJflj4oganBn44CBanBlZ+OAgWJtcOOAgWdpZuOAgXBuZ+OAgXR4dOOAgWluaeOAgXBkZiDmqpTmoYhkZGS2D8X7iDe0uHriEiGBff9X+wr7BVsB93g3xtf3atV/ww=='
    __eventValidation = '/wEWBgLZiqv4DwKn07zPAwKl1bKzCQKE8/26DALH5vq4BgLYk4ODBe3iwTC0koo+bObEaw9EA6detDBG/UpqnmQTMnrHxxJw'
    
    def __init__(self, 使用者名稱=預設名稱, 信箱=預設信箱):
        self.__使用者名稱 = 使用者名稱
        self.__信箱 = 信箱
        self.__post資料 = {
                '__VIEWSTATE': self.__viewState,
                '__EVENTVALIDATION': self.__eventValidation,
                'txtUserName': 使用者名稱,
                'txtEmail': 信箱,
                'lnkbtnUpload': '確認上傳'
            }
    
    @property
    def 使用者名稱(self):
        return self.__使用者名稱
    @使用者名稱.setter
    def 使用者名稱(self, 使用者名稱):
        self.__使用者名稱 = 使用者名稱
        self.__post資料['txtUserName'] = 使用者名稱

    @property
    def 信箱(self):
        return self.__信箱
    @信箱.setter
    def 信箱(self, 信箱):
        self.__信箱 = 信箱
        self.__post資料['txtEmail'] = 信箱
    
    def 上傳(self, 檔案列表):
        結果 = []
        分頁 = requests.Session()
        for 檔案 in 檔案列表:
            分頁.post(self.ibon網域+self.填表頁面, data=self.__post資料, files={'fuFile': 檔案})
            回覆 = 分頁.get(self.ibon網域+self.查詢頁面)
            資料 = etree.HTML(回覆.text)
            取件代碼 = 資料.xpath('//*[@id="thisform"]/div[1]/table[2]/tr[2]/td[3]/p')[0].text.strip()
            列印期限 = 資料.xpath('//*[@id="thisform"]/div[1]/table[2]/tr[2]/td[2]')[0].text.strip()
            QRCode請求位址 = 資料.xpath('//*[@id="imgQRCode"]//@src')[0]
            QRCode = 分頁.get(self.ibon網域+QRCode請求位址).content
            結果.append({'取件代碼': 取件代碼, '列印期限': 列印期限, 'QRCode': QRCode})
        return tuple(結果)
        

class FamiPort列印小幫手(object):
    pass


class 萊爾富列印小幫手(object):
    pass