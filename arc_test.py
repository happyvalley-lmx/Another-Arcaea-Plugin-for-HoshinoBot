import requests
import json
import os
import math
from another_arcaea.config.apiconfig import api_link,token
from PIL import Image, ImageFont, ImageDraw

nowdir = os.getcwd()
print(nowdir)
api_token = '&token=' + token

def b30():
    user_id = input('输入用户ID:')
    request_link = api_link + '/user/best30?user=' + user_id + '&withrecent=true&withsonginfo=true' + api_token
    req_data = requests.get(request_link)
    req_data_json = json.loads(req_data.content)
    username = req_data_json['content']['account_info']['name']
    ptt = math.floor((req_data_json['content']['best30_avg'] + req_data_json['content']['recent10_avg']) / 2 * 100) / 100
    print(ptt)

    image = Image.new('RGB', (800, 1000), (0,0,0)) # 设置画布大小及背景色
    draw = ImageDraw.Draw(image)
    font_main = ImageFont.truetype(nowdir + '\\another_arcaea\\NotoSansSC-Regular.otf', 30)
    draw.text((10, 5), f'{username}     PTT:{ptt}', 'white', font_main)
    
    font = ImageFont.truetype(nowdir + '\\another_arcaea\\NotoSansSC-Regular.otf', 20) # 设置字体及字号
    fontx = 10
    draw.text((fontx, 50), f'单曲PTT|难度|定数|分数|乐曲名称', 'white', font)
    fonty = 80
    i = 0
    for b30_single in req_data_json['content']['best30_list']:
        rating = math.floor(b30_single['rating'] * 100) / 100
        diff_raw = b30_single['difficulty']
        if diff_raw == 3:
            diff = 'BYD'
        elif diff_raw == 2:
            diff = 'FTR'
        elif diff_raw == 1:
            diff = 'PRS'
        else:
            diff = 'PST'
        rating_ori = req_data_json['content']['best30_songinfo'][i]['rating'] / 10
        score = b30_single['score']
        s_name = req_data_json['content']['best30_songinfo'][i]['name_en']

        draw.text((fontx, fonty), f'No.{i+1}:[{rating}|{diff}|{rating_ori}|{score}] {s_name}', 'white', font)
        fonty = fonty + 30
        i += 1
    
    image.save(f'b30_pic\\{user_id}.jpg') # 保存图片

b30()