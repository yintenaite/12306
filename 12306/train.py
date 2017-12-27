import requests
import sys
import damatu
import message
import json
import time
import re
'''
硬座 1  
硬卧 3  
软卧 4


成人票 1
儿童票 2
学生票 3


二代身份证 1
护照 B

座位编号,0,票类型,乘客名,证件类型,证件号,手机号码,保存常用联系人(Y或N)  

硬卧,0 ，passenger_type，passenger_name，passenger_id_type_code，passenger_id_no，mobile_no，N


乘客名,证件类型,证件号,乘客类型 

passenger_name，passenger_id_type_code，passenger_id_no，passenger_type_
'''

class Train(object):

    def __init__(self):

        # 禁用安全请求警告
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        self.session = requests.session()
        self.session.headers = {
                    'Host': 'kyfw.12306.cn',
                    'Origin' : 'https://kyfw.12306.cn',
                    'X-Requested-With' : 'XMLHttpRequest',
                    'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer' : 'https://kyfw.12306.cn/otn/login/init',
                    'Accept': '*/*',
                    'Accept-Encoding' : 'gzip, deflate, br',
                    'Accept-Language' : 'zh-CN,zh;q=0.8',
                    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36',
        }
        self.session.verify = False
        self.stationNameToCode = dict()
        self.stationCodeToName = dict()
        self.trainDate = ''
        self.fromStationName = ''
        self.fromStationCode = ''
        self.toStationName = ''
        self.toStationCode = ''
        self.fromStationTelecode = ''
        self.toStationTelecode = ''
        self.initStations()
        self.trainSecretStr = ''
        self.trainNo = ''
        self.trainCode = ''
        self.leftTicket = ''
        self.seatType = ''
        self.trainLocation = ''
        self.submitToken = ''
        self.passengerTicketStr = ''
        self.oldPassengerStr = ''
        self.orderId = ''
        self.seatMap = {
            'yingzuo' : '1',
            'yingwo' : '3',
            'ruanwo' : '4'
        }
        self.canChooseSeat = dict()

    def getCoordinate(self):
        num = input('请输入图片序号:')
        coordinates = ['8,44','108,46','186,43','249,44','26,120','107,120','185,125','253,119']
        cList = list(map(lambda x : coordinates[int(x)-1] , num))
        return '|'.join(cList)

    def captchaCheck(self):

        captchaErrorCount = 0
        print('正在识别验证码...')
        while True:
            if captchaErrorCount > 5:
                print('验证码失败次数超过限制，登录失败，退出程序')
                sys.exit()
            # 获取验证码
            captchaRes = self.session.get(
                'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.46630622142659206')
            captcha = captchaRes.content
            with open(message.captchaDownloadName, 'wb') as f:
                f.write(captcha)

            captchaStr = damatu.DamatuApi(message.damaUserName,message.damaPassword).decode(message.captchaDownloadName, 287)
            #captchaStr = self.getCoordinate()
            print(captchaStr)
            captchaStr = captchaStr.replace('|', ',')
            captchaStr = requests.utils.requote_uri(captchaStr)
            data = {
                'answer': captchaStr,
                'login_site' :'E',
                'rand': 'sjrand'
            }
            #验证验证码
            response = self.session.post('https://kyfw.12306.cn/passport/captcha/captcha-check', data = data)
            print(response.text)
            result = response.json()
            if result['result_code'] == '4':
                print('识别验证码成功')
                break
            else:
                #print('识别验证码失败')
                captchaErrorCount += 1

    def secLoginVerify(self,newapptk):

        print('第二次验证')
        newAppTkErrorCount = 0
        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        data = {
            'tk': newapptk
        }
        while True:
            if newAppTkErrorCount > 5:
                print('newAppTk获取失败,退出程序')
                sys.exit()
            response = self.session.post(url, data = data)
            try:
                verifyResult = response.json()
                print(verifyResult)
                return verifyResult
            except json.decoder.JSONDecodeError:
                newAppTkErrorCount += 1

    def login(self):

        # 1 伪装cookie++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        jsUrl = 'https://kyfw.12306.cn/otn/HttpZF/GetJS'
        setCookieCountError = 0
        while True:
            if setCookieCountError > 3:
                print('设置cookie失败，退出程序')
                sys.exit()
            try:
                response = self.session.get(jsUrl)
                pattern = re.compile(r'algID=(.*?)&')
                algID = pattern.findall(response.text)
                url = 'https://kyfw.12306.cn/otn/HttpZF/logdevice?algID=WYEdoc45yu&hashCode=EhTtj7Znzyie6I21jpgekYReLAnA8fyGEB4VlIGbF0g&FMQw=0&q4f3=zh-CN&VPIf=1&custID=133&VEek=unknown&dzuS=20.0%20r0&yD16=0&EOQP=895f3bf3ddaec0d22b6f7baca85603c4&lEnu=3232235778&jp76=e8eea307be405778bd87bbc8fa97b889&hAqN=Win32&platform=WEB&ks0Q=2955119c83077df58dd8bb7832898892&TeRS=728x1366&tOHY=24xx768x1366&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&0aew={}&E3gR=abfdbb80598e02f8aa71b2b330daa098&timestamp={}'.format(
                    self.session.headers['User-Agent'], str(round(time.time() * 1000)))
                response = self.session.get(requests.utils.requote_uri(url))
                pattern = re.compile('\(\'(.*?)\'\)')
                userVerify3 = eval(pattern.findall(response.text)[0])
                # print('设置cookie')
                # print(userVerify3)
                railExpiration = userVerify3['exp']
                railDeviceId = userVerify3['dfp']
                self.session.cookies['RAIL_EXPIRATION'] = railExpiration
                self.session.cookies['RAIL_DEVICEID'] = railDeviceId
                break
            except:
                setCookieCountError += 1

        #2 做验证码验证++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        self.captchaCheck()


        #3 用户名密码登陆++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        print('用户名密码登录')
        loginUrl = 'https://kyfw.12306.cn/passport/web/login'
        data = {
            'username': message.userName,
            'password': message.password,
            'appid' : 'otn'
        }
        response = self.session.post(loginUrl, data = data)
        loginResult = response.json()
        print(loginResult)
        if loginResult['result_code'] != 0:
            print('用户名密码错误(loginCheck) {}'.format(loginResult['result_code']))
            sys.exit()
        self.session.cookies['uamtk'] = loginResult['uamtk']

        #4 用户登录第一次验证+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        data = {
            'appid': 'otn'
        }
        response = self.session.post(url, data=data,)
        userVerify = response.json()
        print('第一次验证')
        print(userVerify)
        if userVerify['result_code'] != 0:
            print('验证失败(uamtk) code:{}'.format(userVerify['result_code']))

        #5 用户登录第二次验证++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        newapptk = userVerify['newapptk']
        userVerify2 = self.secLoginVerify(newapptk)
        print('验证通过，用户为:{}'.format(userVerify2['username']))

    def downloadStations(self):
        print('正在下载城市代码...')
        stationUrl = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9035'
        response = self.session.get(stationUrl)
        pattern = re.compile('\'(.*?)\'')
        with open(message.stationDownloadName, 'w', encoding='utf8') as f:
            f.write(pattern.findall(response.text)[0].lstrip('@'))
        print('城市代码下载完毕')

    def initStations(self):
        errorCount = 0
        while True:
            if errorCount > 3:
                print('读取车站代码失败，退出程序')
                sys.exit()
            try:
                with open(message.stationDownloadName, 'r', encoding='utf8') as f:
                    stationsStr = f.read()
                stations = stationsStr.split('@')
                for s in stations:
                    tempStationSplit = s.split('|')
                    self.stationNameToCode[tempStationSplit[1]] = tempStationSplit[2]
                    self.stationCodeToName[tempStationSplit[2]] =tempStationSplit[1]
                return
            except:
                print('车站代码读取失败,正在重试...')
                errorCount += 1
                self.downloadStations()

    def findTicket(self):
        #1 输入站名坐车时间++++++++++++++++++++++++++++++++++++++++++++++++

        self.trainDate = input('坐车时间(2000-01-01):')
        while True:
            stationNames = []
            stationNames.append(input('起点站:'))
            stationNames.append(input('终点站:'))
            try:
                stationCode = list(map(lambda  x : self.stationNameToCode[x],stationNames))
                self.fromStationName = stationNames[0]
                self.fromStationCode = stationCode[0]
                self.toStationName = stationNames[1]
                self.toStationCode = stationCode[1]
                break
            except KeyError:
                print('车站名称错误,重新输入')

        #2 查询车次+++++++++++++++++++++++++++++++++++++++++++++++++++++++

        queryUrl = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
            self.trainDate, self.fromStationCode, self.toStationCode)
        findTicketError = 0
        while True:
            if findTicketError > 5:
                print('查询出现错误，退出程序')
                sys.exit()
            try:
                response = self.session.get(queryUrl)
                trainList = response.json()['data']['result']
                break
            except (json.decoder.JSONDecodeError,KeyError):
                findTicketError += 1
        if len(trainList) > 0:
            '''
            secretstr 0
            内容是 预订 1
            不知道什么串加车次 2
            车次 3
            始发站 4
            终点站 5 
            要坐的站 6
            要到的站 7
            出发时间 8
            到达时间 9
            历时 10
            是否可以预订（Y可以 N和IS_TIME_NOT_BUY 不可以）   11  
            leftTicket 12
            日期20171216 13
            trainLocation 15
            软卧 23
            硬卧 28
            硬座 29
            '''
            #3 过滤车次++++++++++++++++++++++++++++++++++++++++++++++++
            filterTrainList = []
            for train in trainList:
                trainDetailSplit = train.split('|')
                if trainDetailSplit[11] == 'Y' and (not(trainDetailSplit[23] == ''or trainDetailSplit[23] == '无') or not(trainDetailSplit[28] == ''or trainDetailSplit[28] == '无') or not(trainDetailSplit[29] == ''or trainDetailSplit[29] == '无')):
                    filterTrainList.append(train)
            if len(filterTrainList) > 0:
               self.printTrainList(filterTrainList)
               #4 锁定用户输入车次++++++++++++++++++++++++++++++++++++++
               while True:
                   trainName = input('请输入要预订的列车编号:').upper()
                   for filterTrain in filterTrainList:
                        trainDetailSplit = filterTrain.split('|')
                        if trainDetailSplit[3] == trainName:
                            self.trainSecretStr = trainDetailSplit[0]
                            self.trainNo = trainDetailSplit[2]
                            self.trainCode = trainDetailSplit[3]
                            self.leftTicket = trainDetailSplit[12]
                            self.fromStationTelecode = trainDetailSplit[6]
                            self.toStationTelecode = trainDetailSplit[7]
                            self.leftTicket = trainDetailSplit[12]
                            self.trainLocation = trainDetailSplit[15]
                            if trainDetailSplit[23] != '' and trainDetailSplit[23] != u'无':
                                self.canChooseSeat['ruanwo'] = self.seatMap['ruanwo']
                            if trainDetailSplit[28] != '' and trainDetailSplit[28] != u'无':
                                self.canChooseSeat['yingwo'] = self.seatMap['yingwo']
                            if trainDetailSplit[29] != '' and trainDetailSplit[29] != u'无':
                                self.canChooseSeat['yingzuo'] = self.seatMap['yingzuo']
                            return
                   print('输入错误，请重新输入')
            else:
                print('{},{}到{} 没有可买车次（已售完或暂停车次）'.format(self.trainDate, self.fromStationName, self.toStationName))
        else:
            print('{},{}到{} 无车次'.format(self.trainDate,self.fromStationName,self.toStationName))

    def printTrainList(self,filterTrainList):
        print('  ┌───┬─────┬─────┬───┬───┬───┬──┬──┬──┐')
        print('  │车编号│始发站名称│终点站名称│出发时│到站时│总用时│软卧│硬卧│硬座│')
        print('  ├───┴─────┴─────┴───┴───┴───┴──┴──┴──┤')
        print('  ├───┬─────┬─────┬───┬───┬───┬──┬──┬──┤')
        for filterTrain in filterTrainList:
            ft = filterTrain.split('|')
            fromStationName = self.stationCodeToName[ft[6]]
            toStationName = self.stationCodeToName[ft[7]]
            fromStationName = '  ' * (5 - len(fromStationName)) + fromStationName
            toStationName = '  ' * (5 - len(toStationName)) + toStationName
            seats = dict()
            seats['ruanwo'] = ft[23]
            seats['yingwo'] = ft[28]
            seats['yingzuo'] = ft[29]
            for key, value in seats.items():
                if value == '' or value == '无':
                    seats[key] = '-'
                elif value == '有':
                    seats[key] = 'YES'
            print('  │%6s│%3s│%3s│%6s│%6s│ %4s│%4s│%4s│%4s│' % (ft[3], fromStationName, toStationName, ft[8], ft[9], ft[10], seats['ruanwo'], seats['yingwo'], seats['yingzuo']))
            print('  ├───┼─────┼─────┼───┼───┼───┼──┼──┼──┤')
        print('  └───┴─────┴─────┴───┴───┴───┴──┴──┴──┘')

    def choosePassenger(self,message):
        passengerList = message['data']['normal_passengers']
        print('账户可订票乘客: {}'.format(' '.join(list(map(lambda x: x['passenger_name'], passengerList)))))
        pessengerName = input('请输入订票乘客:')
        while True:
            pessengerDetail = dict()
            for p in passengerList:
                if pessengerName == p['passenger_name']:
                    pessengerDetail = {
                        'passenger_flag' : p['passenger_flag'],
                        'passenger_type' : p['passenger_type'],
                        'passenger_name' : p['passenger_name'],
                        'passenger_id_type_code' : p['passenger_id_type_code'],
                        'passenger_id_no' : p['passenger_id_no'],
                        'mobile_no' : p['mobile_no']
                    }
                    return pessengerDetail
            pessengerName = input('乘客姓名输入错误，请重新输入:')

    def chooseSeat(self):
        seat = input('请输入座位:')
        while True:
            if seat == '硬座':
                seat = 'yingzuo'
            if seat == '硬卧':
                seat = 'yingwo'
            if seat == '软卧':
                seat = 'ruanwo'
            for i,key in enumerate(self.canChooseSeat):
                if seat == key:
                    self.seatType = self.canChooseSeat[key]
                    return
            seat = input('输入座位有误，请重新输入:')

    def bookingTicket(self):

        # 1 checkUser +++++++++++++++++++++++++++++++++++++++++++++

        self.session.headers['Referer'] = 'https://kyfw.12306.cn/otn/leftTicket/init'
        userCheckError = 0
        while True:
            if userCheckError > 2:
                print('用户登录检测失败，退出程序')
                sys.exit()
            url = 'https://kyfw.12306.cn/otn/login/checkUser'
            try:
                result = self.session.post(url).json()
                print('验证登录状态checkUser')
                print(result)
                if not result['data']['flag'] :
                    print('用户未登录checkUser')
                    userCheckError += 1
                    self.login()
                    continue
                print('验证登录状态成功checkUser')
                break
            except json.decoder.JSONDecodeError:
                userCheckError += 1


        # 2 submitOrderRequest+++++++++++++++++++++++++++++++++++++
        print('正在提交订单...')
        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {
            'secretStr':self.trainSecretStr,
            'train_date':self.trainDate,
            'back_train_date':time.strftime("%Y-%m-%d", time.localtime(time.time())),
            'tour_flag':'dc',  # dc 单程
            'purpose_codes':'ADULT',  # adult 成人票
            'query_from_station_name':self.fromStationName,
            'query_to_station_name':self.toStationName
        }
        data = str(data)[1:-1].replace(':','=').replace(',','&').replace(' ','').replace('\'','')
        data = requests.utils.requote_uri(data)
        result = self.session.post(url,data=data).json()
        print('submitOrderRequest+++++')
        print(result)
        if not result['status']:
            print('提交订单失败 status = {}'.format(result['status']))
            sys.exit()
        print('提交订单成功')

        # 3 initDC+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = '_json_att='
        response = self.session.post(url, data = data)
        pattern = re.compile('globalRepeatSubmitToken = \'(.*?)\'')
        pattern2 = re.compile("key_check_isChange':'(.*?)'")
        self.submitToken = pattern.findall(response.text)[0]
        self.keyCheckIsChange = pattern2.findall(response.text)[0]
        print('token:{}'.format(self.submitToken))
        print('key_check_isChange:{}'.format(self.keyCheckIsChange))



        # 4 getPassengerDTOs++++++++++++++++++++++++++++++++++++++++++++++++++++++

        print('正在获取乘客信息')
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {
            '_json_att' : '',
            'REPEAT_SUBMIT_TOKEN' : self.submitToken
        }
        response = self.session.post(url, data = data)
        result = response.json()
        #print(result)
        print('获取信息成功')
        pd = self.choosePassenger(result)
        self.chooseSeat()

        # 5 checkOrderInfo++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        print('正在验证订单...')
        self.passengerTicketStr = self.seatType + ',' + pd['passenger_flag'] + ',' + pd['passenger_type'] + ',' + pd['passenger_name'] + ',' + pd['passenger_id_type_code'] + ',' + pd['passenger_id_no'] + ',' + pd['mobile_no'] + ',N'

        self.oldPassengerStr =  pd['passenger_name'] + ',' + pd['passenger_id_type_code'] + ',' + pd['passenger_id_no'] + ',' + pd['passenger_type'] + '_'

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data = 'cancel_flag=2&bed_level_order_num=000000000000000000000000000000&passengerTicketStr={}&oldPassengerStr={}_&tour_flag=dc&randCode=&whatsSelect=1&_json_att=&REPEAT_SUBMIT_TOKEN={}'.format(
            self.passengerTicketStr,self.oldPassengerStr,self.submitToken
        )
        data = requests.utils.requote_uri(data)
        checkOrderRrrorCount = 0
        while True :
            if checkOrderRrrorCount > 3:
                print('验证订单失败，退出程序')
                sys.exit()
            response = self.session.post(url, data = data)
            result = response.json()
            if result['data']['submitStatus']:
                print('订单验证成功')
                break

        # 6 getQueueCount+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        dateGMT = time.strftime('%a %b %d %Y %H:%M:%S  GMT+0800', time.strptime(self.trainDate, '%Y-%m-%d'))
        # data = 'train_date={}&train_no={}&stationTrainCode={}&seatType={}&fromStationTelecode={}&toStationTelecode={}&leftTicket={}&purpose_codes=00&train_location={}&_json_att=&REPEAT_SUBMIT_TOKEN={}'.format(
        #     dateGMT,self.trainNo,self.trainCode,self.seatType,self.fromStationTelecode,self.toStationTelecode,self.leftTicket,self.trainLocation,self.submitToken
        # )
        data = {
            'train_date' : dateGMT,
            'train_no' : self.trainNo,
            'stationTrainCode' : self.trainCode,
            'seatType' : self.seatType,
            'fromStationTelecode' : self.fromStationTelecode,
            'toStationTelecode' : self.toStationTelecode,
            'leftTicket' : self.leftTicket,
            'purpose_codes' : '00',
            'train_location' : self.trainLocation,
            '_json_att' : '',
            'REPEAT_SUBMIT_TOKEN' : self.submitToken
        }
        response = self.session.post(url, data = data)
        print('getQueueCount++++++')
        result = response.json()
        print(result)

        # 7 confirmSingleForQueue++++++++++++++++++++++++++++++++++++++++++++++++++

        #https://kyfw.12306.cn/otn/confirmPassenger/confirmSingle
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data = {
            'passengerTicketStr' : self.passengerTicketStr,
            'oldPassengerStr' : self.oldPassengerStr,
            'randCode' : '',
            'purpose_codes' : '00',
            'key_check_isChange' : self.keyCheckIsChange,
            'leftTicketStr' : self.leftTicket,
            'train_location' : self.trainLocation,
            'choose_seats' : '',
            'seatDetailType' : '000',
            'whatsSelect' : '1',
            'roomType' : '00',
            'dwAll' : 'N',
            '_json_att' : '',
            'REPEAT_SUBMIT_TOKEN' : self.submitToken
        }
        qeueErrorCount = 0
        while True:
            if qeueErrorCount > 3:
                print('confirmSingleForQueue错误，退出程序')
                sys.exit()
            response = self.session.post(url, data = data)
            try:
                result = response.json()
                print('confirmSingleForQueue++++++')
                print(result)
                if not result['data']['submitStatus']:
                    print('订票失败，退出程序')
                    sys.exit()
                else:
                    break
            except:
                qeueErrorCount += 1

        # 8 queryOrderWaitTime+++++++++++++++++++++++++++++++++++++++++

        waitTimeErrorCount = 0
        while True:
            print('queryOrderWaitTime+++++++')
            if waitTimeErrorCount > 10:
                print('请求次数过多，退出程序')
                sys.exit()
            url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random={}&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN={}'.format(
                str(round(time.time() * 1000)),self.submitToken)
            response = self.session.get(url)
            result = response.json()
            print(result)
            resultCode = result['data']['waitTime']
            if resultCode == -1:
                self.orderId = result['data']['orderId']
                break
            elif resultCode == -2:
                print('取消次数过多，今日不能继续订票')
                sys.exit()
            else:
                waitTimeErrorCount += 1
                time.sleep(1)

        # 8 resultOrderForDcQueue+++++++++++++++++++++++++++++++++++++++++

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
        data = 'orderSequence_no={}&_json_att=&REPEAT_SUBMIT_TOKEN={}'.format(self.orderId,self.submitToken)
        resultOrderErrorCount = 0
        while True:
            if resultOrderErrorCount > 3:
                print('查询订单错误')
                sys.exit()
            response = self.session.post(url, data = data)
            try:
                result = response.json()
                print(result)
                if result['data']['submitStatus']:
                    print('订票成功，请登录12306查看')
                    break
            except json.decoder.JSONDecodeError:
                resultOrderErrorCount += 1

t = Train()
t.login()
t.findTicket()
t.bookingTicket()
