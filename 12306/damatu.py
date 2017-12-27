# python版本3.4

import hashlib
import urllib.request
import urllib
import json
import base64
import message


def md5str(str):  # md5加密字符串
    m = hashlib.md5(str.encode(encoding="utf-8"))
    return m.hexdigest()


def md5(byte):  # md5加密byte
    return hashlib.md5(byte).hexdigest()


class DamatuApi():
    ID = message.damaId
    KEY = message.damaKey
    HOST = 'http://api.dama2.com:7766/app/'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def getSign(self, param=b''):
        return (md5(bytes(self.KEY, encoding="utf8") + bytes(self.username, encoding="utf8") + param))[:8]

    def getPwd(self):
        return md5str(self.KEY + md5str(md5str(self.username) + md5str(self.password)))

    def post(self, path, params={}):
        data = urllib.parse.urlencode(params).encode('utf-8')
        url = self.HOST + path
        response = urllib.request.Request(url, data)
        return urllib.request.urlopen(response).read()


    # 上传验证码 参数filePath 验证码图片路径 如d:/1.jpg type是类型，查看http://wiki.dama2.com/index.php?n=ApiDoc.Pricedesc  return 是答案为成功 如果为负数 则为错误码
    def decode(self, filePath, type):
        f = open(filePath, 'rb')
        fdata = f.read()
        filedata = base64.b64encode(fdata)
        f.close()
        data = {'appID': self.ID,
                'user': self.username,
                'pwd': self.getPwd(),
                'type': type,
                'fileDataBase64': filedata,
                'sign': self.getSign(fdata)
                }
        res = self.post('d2File', data)
        res = str(res, encoding="utf-8")
        jres = json.loads(res)
        if jres['ret'] == 0:
            # 注意这个json里面有ret，id，result，cookie，根据自己的需要获取
            result = ''
            str1 = jres['result']
            if str1.find('|') == -1:
                xy = str1.split(',')
                x = xy[0]
                y = str(int(xy[1]) - 28)
                result = x+','+y
            else:
                temp = str1.split('|')
                for t in temp:
                    xy = t.split(',')
                    x = xy[0]
                    y = str(int(xy[1]) - 20)
                    result += x + ',' + y + '|'
                result = result[:-1]
            return (result)
        else:
            return jres['ret']