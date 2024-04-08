import random
from time import localtime
from requests import get, post
from datetime import datetime, date, timedelta
from zhdate import ZhDate
import sys
import os


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token


# 顺序读取json数组数据
def extract_element_from_json(obj, path):
    '''
    输入关键字，就可以将关键字的值信息存放在列表中并输出
    如果关键字是对象名，则返回的对象字典信息到列表中
    如果关键字是列表名，则返回的列表信息到列表中（返回双重列表）
    '''

    def extract(obj, path, ind, arr):
        '''
    	从一个嵌套的字典中提取一个元素，并返回到列表中。
        params: obj - dict - 输入字典
        params: path - list - 构成JSON路径的字符串列表
        params: ind - int - 起始索引
        params: arr - 列表 - 输出列表
    	'''
        key = path[ind]
        if ind + 1 < len(path):
            if isinstance(obj, dict):
                if key in obj.keys():
                    extract(obj.get(key), path, ind + 1, arr)
                else:
                    arr.append(None)
            elif isinstance(obj, list):
                if not obj:
                    arr.append(None)
                else:
                    for item in obj:
                        extract(item, path, ind, arr)
            else:
                arr.append(None)
        if ind + 1 == len(path):
            if isinstance(obj, list):
                if not obj:
                    arr.append(None)
                else:
                    for item in obj:
                        arr.append(item.get(key, None))
            elif isinstance(obj, dict):
                arr.append(obj.get(key, None))
            else:
                arr.append(None)
        return arr

    if isinstance(obj, dict):
        return extract(obj, path, 0, [])
    elif isinstance(obj, list):
        outer_arr = []
        for item in obj:
            outer_arr.append(extract(item, path, 0, []))
        return outer_arr


def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    full_url = "region_url = " + region_url
    print(full_url)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]

    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    full_url = "weather_now_url = " + weather_url
    print(full_url)
    response = get(weather_url, headers=headers).json()
    print(response)
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]

    weather_url = "https://devapi.qweather.com/v7/weather/3d?location={}&key={}".format(location_id, key)
    full_url = "weather_3d_url = " + weather_url
    print(full_url)
    response = get(weather_url, headers=headers).json()
    print(response)
    # 明日天气
    nextweather = response["daily"][1]["textDay"]
    # 明日温度
    nextmin_temp = response["daily"][1]["tempMin"] + u"\N{DEGREE SIGN}" + "C"
    nextmax_temp = response["daily"][1]["tempMax"] + u"\N{DEGREE SIGN}" + "C"
    # 最高气温
    max_temp = response["daily"][0]["tempMax"] + u"\N{DEGREE SIGN}" + "C"
    # 最低气温
    min_temp = response["daily"][0]["tempMin"] + u"\N{DEGREE SIGN}" + "C"
    # 日出时间
    sunrise = response["daily"][0]["sunrise"]
    # 日落时间
    sunset = response["daily"][0]["sunset"]


    url = "https://devapi.qweather.com/v7/air/now?location={}&key={}".format(location_id, key)
    full_url = "air_now_url = " + url
    print(full_url)
    response = get(url, headers=headers).json()
    print(response)
    # 空气质量
    category = response["now"]["category"]
    # pm2.5
    pm2p5 = response["now"]["pm2p5"]

    id = random.randint(1, 16)
    url = "https://devapi.qweather.com/v7/indices/1d?location={}&key={}&type={}".format(location_id, key, id)
    full_url = "indices_today_url = " + url
    print(full_url)
    response = get(url, headers=headers).json()
    print(response)
    proposal = ""
    if response["code"] == "200":
        proposal += response["daily"][0]["text"]
    print(proposal)
    return nextweather, nextmin_temp, nextmax_temp, weather, temp, max_temp, min_temp, wind_dir, sunrise, sunset, category, pm2p5, proposal

def get_tianhang():
    try:
        key = config["tian_api"]
        url = "http://api.tianapi.com/mingyan/index?key={}".format(key)
        print("tianhang = "+url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Content-type': 'application/x-www-form-urlencoded'

        }
        response = get(url, headers=headers).json()
        if response["code"] == 200:
            chp = response["newslist"][0]["content"]
        else:
            chp = ""
    except KeyError:
        chp = ""
    return chp

def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)

    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day


def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en


def send_message(to_user, access_token, region_name, nextweather, nextmin_temp, nextmax_temp, weather, temp,
                 wind_dir, note_ch, note_en, max_temp, min_temp,sunrise, sunset, category, pm2p5, proposal, chp):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取所有生日数据
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    # 获取明日日期
    # today = datetime.now().strftime('%Y-%m-%d')
    nextdate = datetime.now() + timedelta(days=1)
    tDate = nextdate.strftime('%Y-%m-%d')
    print("nextdate = ",tDate)
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": "#FF3333"
            },
            "region": {
                "value": region_name,
                "color": "#FF8800"
            },
            "nextdata": {
                "value": tDate,
                "color": "#FF8800"
            },
            "nextweather": {
                "value": nextweather,
                "color": "#FF8800"
            },
            "nextmin_temp": {
                "value": nextmin_temp,
                "color": "#FF8800"
            },
            "nextmax_temp": {
                "value": nextmax_temp,
                "color": "#FF8800"
            },
            "weather": {
                "value": weather,
                "color": "#FF8800"
            },
            "temp": {
                "value": temp,
                "color": "#FF8800"
            },
            "wind_dir": {
                "value": wind_dir,
                "color": "#FF8800"
            },
            "love_day": {
                "value": love_days,
                "color": "#FF8800"
            },
            "note_en": {
                "value": note_en,
                "color": "#FF8800"
            },
            "note_ch": {
                "value": note_ch,
                "color": "#FF8800"
            },
            "max_temp": {
                "value": max_temp,
                "color": "#FF8800"
            },
            "min_temp": {
                "value": min_temp,
                "color": "#FF8800"
            },
            "sunrise": {
                "value": sunrise,
                "color": "#FF8800"
            },
            "sunset": {
                "value": sunset,
                "color": "#FF8800"
            },
            "category": {
                "value": category,
                "color": "#FF8800"
            },
            "pm2p5": {
                "value": pm2p5,
                "color": "#FF8800"
            },
            "proposal": {
                "value": proposal,
                "color": "#FF8800"
            },
            "chp": {
                "value": chp,
                "color": "#FF8800"
            }
        }
    }
    for key, value in birthdays.items():
        # 获取距离下次生日的时间
        birth_day = get_birthday(value["birthday"], year, today)
        if birth_day == 0:
            birthday_data = "今天是您的生日哦，祝您生日快乐~~"
        else:
            birthday_data = "距离您的生日还有{}天~~".format(birth_day)
        # 将生日数据插入data
        data["data"][key] = {"value": birthday_data, "color": "#FF8800"}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]
    nextweather, nextmin_temp, nextmax_temp, weather, temp, max_temp, min_temp, wind_dir, sunrise, sunset, category, pm2p5, proposal = get_weather(region)
    note_ch = config["note_ch"]
    note_en = config["note_en"]
    if note_ch == "" and note_en == "":
    # 获取词霸每日金句
       note_ch, note_en = get_ciba()
    chp = get_tianhang()
    print("chp = " + chp)
    # 公众号推送消息
    for user in users:
       send_message(user, accessToken, region, nextweather, nextmin_temp, nextmax_temp, weather, temp,
                   wind_dir, love_days, note_ch, note_en, max_temp, min_temp, sunrise, sunset, category, pm2p5, proposal, chp)
    os.system("pause")
