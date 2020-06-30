import email.utils # for rfc2822 formatted current timestamp
import requests
from datetime import datetime
import time
class CometClient(object):

    def __init__(self, callback, last_modified=None):
        self.callback = callback
        if last_modified is None:
            self.last_modified = email.utils.formatdate()
        else:
            self.last_modified = last_modified
        self.etag = 0

    def listen(self, url):
        while True:
            self._get_request(url)

    def get(self, url, timeout):
        self._get_request(url, timeout)

    def _get_request(self, url, Timeout = 180):
        try:
            resp = requests.get(url, headers={
                    'If-None-Match': str(self.etag),
                    'If-Modified-Since': str(self.last_modified)}, timeout=Timeout)
            try:
                self.last_modified = resp.headers['Last-Modified']
                self.etag = resp.headers['Etag']
            except:
                pass
            self.handle_response(resp.content)
            self.errorCount = 0;
            #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] +  " Got message " + resp.content)
        except requests.exceptions.Timeout: # it is planned timeout to make sure it is alive on reconnect
            #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] +  " Connection Timeout")
            pass
        except requests.exceptions.ConnectionError:
            print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] +  " Connection Error")
            self.errorCount += 1
            time.sleep(1)
            if (self.errorCount > 3):
                raise Exception('Too many connection failures. Restart needed')
            pass
        except:
            print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] +  " Unknown exception (TODO to find out)")
            self.errorCount += 1
            time.sleep(1)
            if (self.errorCount > 3):
                raise Exception('Too many exceptions. Restart needed')
            pass

    def handle_response(self, response):
        self.callback(response)
