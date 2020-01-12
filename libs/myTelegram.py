# -*- coding: utf-8 -*-
import sys, os
import json
import httplib2
import time
import urllib
import subprocess
import re
sys.path.append('/home/scripts/libs')
from MultipartFormdataEncoder import MultipartFormdataEncoder
from myLogs import myLogs
from myFCM import myFCM
from myConfig import myConfig

class myTelegram:
    TOKEN = myConfig.get('telegram', 'token')
    URL = "https://api.telegram.org/bot{}/"
    
    def __init__(self):
        self.URL = self.URL.format(self.TOKEN)
        self.timeout = 5
        self.last_update_id = None

    def setTimeout(self, timeout):
        self.timeout = timeout
    
    def http(self):
        if not hasattr(self, '_http'):
            self._http = httplib2.Http(timeout=self.timeout)
        return self._http

    def enableLog(self):
        self.logHandler = myLogs('telegram-class', 0o666)

    def log(self, data):
        if hasattr(self, 'logHandler'):
            self.logHandler.log(data)

    def get_url(self, url):
        attempts = 20;
        while attempts > 0:
            try:
                response, data = self.http().request(url)
                if response.status == 200:
                    content = data.decode("utf8")
                    return content
            except Exception as e:
                attempts -= 1
                if (attempts < 1):
                    #fcm = myfcm();
                    #data = {"message": {"message":"telegram unable to connect",'cmd': 'showalert','from': 'raspberry'}}

                    #time.sleep(60)
                    raise
            time.sleep(1)
    
    def post_json(self, url, json):
        attempts = 20;
        while attempts > 0:
            try:
                response, data = self.http().request(
                    uri=url,
                    method='POST',
                    headers={'Content-Type': 'application/json; charset=UTF-8'},
                    body=json,
                )
                if response.status == 200:
                    content = data.decode("utf8")
                    return content
            except Exception as e:
                attempts -= 1
                if (attempts < 1):
                    #fcm = myfcm();
                    #data = {"message": {"message":"telegram unable to connect",'cmd': 'showalert','from': 'raspberry'}}

                    #time.sleep(60)
                    raise
            time.sleep(1)


    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js


    def get_updates(self, offset=None):
        tmout = self.timeout - 5
        if tmout < 1:
            tmout = 2
        url = self.URL + "getUpdates?timeout=" + str(tmout)
        if offset:
            url += "&offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js


    def get_last_update_id(self, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)


    def echo_all(self, updates):
        for update in updates["result"]:
            #{'update_id': 968412429, 'channel_post': {'chat': {'type': 'channel', 'title': 'HomePi', 'id': -1001XXXXXXXX}, 'text': 'Hi', 'message_id': 4, 'date': 1541345540}}
            try: 
                if 'message' in update: #direct bot message
                    text = update["message"]["text"]
                    chat = update["message"]["chat"]["id"]
                elif 'channel_post' in update:
                    text = update['channel_post']['text']
                    chat = update["channel_post"]["chat"]["id"]
                    self.log("Got new message in " + str(chat) + ": " + text)
                text = re.compile('\W').split(text)[0]
                subprocess.Popen(['/home/scripts/actions/on-telegram-message.py', text], stdout=subprocess.PIPE).stdout.read().strip()
                #self.send_message('I have got: ' + text, chat)
            except Exception as e:
                self.log("Error processing message:" + str(e))
                #self.send_message('Error : ' + str(e), -1001420XXXXX)
                pass


    def get_last_chat_id_and_text(self, updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return (text, chat_id)


    def send_message(self, text, chat_id, silent = False):
        #text = urllib.parse.quote_plus(text)
        #url = self.URL + "sendMessage?text={}&chat_id={}{}".format(text, chat_id, ('' if silent == False else '&disable_notification=true'))
        url = self.URL + "sendMessage"
        data = {
            'text': text,
            'chat_id': chat_id,
            'disable_notification': silent == False,
            #'reply_markup': {'inline_keyboard': [{
                #'text':'First Btn',
                #'url':'http://dobovo.com',
                #}]}
        }
        #print("sending" + json.dumps(data))
        return self.post_json(url, json.dumps(data));

        #return self.get_url(url)
    
    def send_photo(self, file, chat_id, silent = False):
        try:
            #url = "https://api.telegram.org/bot<Token>/sendPhoto";
            url = self.URL + "sendPhoto"
            if silent == True:
                url += '&disable_notification=true'
            files = [('photo', 'image.jpg', open(file, 'rb'))]
            fields = [('chat_id', str(chat_id))]
            content_type, body = MultipartFormdataEncoder().encode(fields, files)
            response, data = self.http().request(
                url,
                method="POST",
                headers={'Content-Type': content_type + '; charset=UTF-8'},
                body=body
            )
            return response.status == 200
        except:
            return False

    def start(self): #Long Pooling enabled by self.timeout
        while True:
            self.checkServer()
            time.sleep(0.1)

    def checkServer(self):
        updates = self.get_updates(self.last_update_id)
        #print(updates)
        self.processMessage(updates)

    def processMessage(self, updates):
        if len(updates["result"]) > 0:
            self.last_update_id = self.get_last_update_id(updates) + 1
            self.echo_all(updates)

    # old version with requests module
    #def startBot(self):
        #import CometClient
        #self.enableLog()
        #self.log("Starting bot")
        #comet = CometClient.CometClient(self.messageHandler)
        #timeout = 60
        #while True:
            #url = self.URL + "getUpdates?timeout=" + str(timeout-10)
            #if self.last_update_id:
                #url += "&offset={}".format(self.last_update_id)

            ##print("reconnect" + url)
            #comet.get(url, timeout)

    def messageHandler(self, data):
        #print(data)
        js = json.loads(data.decode("utf-8"))
        self.processMessage(js)

    def stop(self):
        pass
        

if __name__ == '__main__':
    tel = myTelegram();
    tel.start()
