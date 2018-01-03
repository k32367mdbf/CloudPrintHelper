# Telegram bot - 雲端列印小幫手

## 功能
- 幫你把檔案傳到ibon，取得列印代碼及QRCode
- 可自訂姓名跟信箱，作為上傳時提供的資訊
- 可自訂預設要詢問的項目，以加快操作流程


## 設定
- 安裝依賴套件
```
pip install -r requirements.txt
```
- 設定TOKEN：修改`config.py`中的`TOKEN`
- 啟動
```
ngrok http 2017
python server.py
```


## 狀態圖
![](./fsm.png)