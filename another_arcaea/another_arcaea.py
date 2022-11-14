import base64
import requests
from .config.apiconfig import api_link,token,bot_db
import pymysql
import json
import math
import os
from PIL import Image, ImageFont, ImageDraw

from nonebot import on_command
from hoshino import R, Service, priv
from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import pic2b64

help_str='''
另一种Arcaea查分插件
基于ArcaeaUnlimitedAPI开发
功能列表：
* 绑定Arcaea账号：
- /arc bind [好友码]
* 查询Arcaea Best30：
- /arc b30
'''

nowdir = os.getcwd()

sv = Service(
    name='another_arcaea', 
    visible=True,
    bundle='娱乐',
    help_= help_str.strip())

headers = {"Authorization":"Bearer "+ token}

@sv.on_prefix(('/arc help'))
async def arc_bind(bot, ev: CQEvent):
    await bot.send(ev, help_str)

@sv.on_prefix(('/arc b30'))
async def arc_b30(bot, ev: CQEvent):
    db_use = pymysql.connect(
        host=bot_db.host,
        port=bot_db.port,
        user=bot_db.user,
        password=bot_db.password,
        database=bot_db.database
    )
    apu_cursor = db_use.cursor()
    qqid = ev.user_id
    apu_getuid_sql = "SELECT QQ,arc_uid FROM grxx WHERE QQ = %s" % (qqid)
    try:
        apu_cursor.execute(apu_getuid_sql)
        result_cx = apu_cursor.fetchall()
        if not result_cx:
            await bot.send(ev, "无法查询到您的数据，请检查是否通过签到功能注册bot功能", at_sender = True)
        elif result_cx[0][1] == None:
            await bot.send(ev, "您还没有绑定您的 Arcaea ID，请先使用绑定功能进行绑定", at_sender = True)
        else:
            user_id = str(result_cx[0][1])
            request_link = api_link + '/user/best30?user=' + user_id + '&withrecent=true&withsonginfo=true'
            req_data = requests.get(request_link, headers=headers)
            req_data_json = json.loads(req_data.content)
            req_status = req_data_json['status']
            if req_status == 0:
                username = req_data_json['content']['account_info']['name']
                ptt = req_data_json['content']['account_info']['rating'] / 100
                b30_avg_ptt = math.floor(req_data_json['content']['best30_avg'] * 1000) / 1000
                r10_avg_ptt = math.floor(req_data_json['content']['recent10_avg'] * 1000) / 1000

                image = Image.new('RGB', (800, 1000), (0,0,0)) # 设置画布大小及背景色
                draw = ImageDraw.Draw(image)
                font_main = ImageFont.truetype(nowdir + '\\hoshino\\modules\\another_arcaea\\NotoSansSC-Regular.otf', 30)
                draw.text((10, 5), f'{username}     PTT:{ptt}(B30/R10:{b30_avg_ptt}/{r10_avg_ptt})', 'white', font_main)
                
                font = ImageFont.truetype(nowdir + '\\hoshino\\modules\\another_arcaea\\NotoSansSC-Regular.otf', 20) # 设置字体及字号
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
                
                image.save(nowdir + f'\\hoshino\\modules\\another_arcaea\\b30_pic\\{user_id}.jpg') # 保存图片
                data = open(nowdir + f'\\hoshino\\modules\\another_arcaea\\b30_pic\\{user_id}.jpg', "rb")
                base64_str = base64.b64encode(data.read())
                img_b64 =  b'base64://' + base64_str
                img_b64 = str(img_b64, encoding = "utf-8")  
                await bot.send(ev, f'[CQ:image,file={img_b64}]')
            else:
                await bot.send(ev, f'查询结果错误，API返回状态码:{req_status}')
    except:
        await bot.send(ev, '查询过程中发生错误')
    db_use.close()

@sv.on_prefix(('/arc bind'))
async def arc_bind(bot, ev: CQEvent):
    #绑定Arcaea好友码到QQ上（使用本地数据库）
    input_id_raw = ev.message.extract_plain_text().strip()
    if len(input_id_raw) == 0:
        await bot.send(ev, '请输入您的SDVX ID！')
    elif input_id_raw.isdigit() == True:
        if int(input_id_raw) < 1000000000:
            input_id = int(input_id_raw)
            db_bot = pymysql.connect(
                host=bot_db.host,
                port=bot_db.port,
                user=bot_db.user,
                password=bot_db.password,
                database=bot_db.database
            )
            arc_cursor = db_bot.cursor()
            qqid = ev.user_id
            arc_getuid_sql = "SELECT QQ,arc_uid FROM grxx WHERE QQ = %s" % (qqid)
            # 先执行一次查询，查询是否已经签到注册过
            try:
                arc_cursor.execute(arc_getuid_sql)
                result_cx = arc_cursor.fetchall()
                arc_bind_sql = "UPDATE `grxx` SET `arc_uid`='%s' WHERE `QQ`='%s'" % (input_id, qqid)
                if not result_cx:
                    await bot.send(ev, "无法查询到您的数据，请检查是否通过签到功能注册bot功能", at_sender = True)
                elif result_cx[0][1] == None:
                    try:
                        arc_cursor.execute(arc_bind_sql)
                        db_bot.commit()
                        await bot.send(ev, f'已为您绑定成功以下ID:{input_id}')
                    except Exception as e:
                        await bot.send(ev, f'查询过程中发生错误:{e}')
                else:
                    await bot.send(ev, f'您已经绑定过了，即将为您重新绑定')
                    try:
                        arc_cursor.execute(arc_bind_sql)
                        db_bot.commit()
                        await bot.send(ev, f'已为您绑定成功以下ID:{input_id}')
                    except Exception as e:
                        await bot.send(ev, f'查询过程中发生错误:{e}')
            except Exception as e:
                await bot.send(ev, f'查询过程中发生错误:{e}')
            db_bot.close()
        else:
            await bot.send(ev, '请输入有效的 Arcaea ID 范围(0~999999999)')
    else:
        await bot.send(ev, '请输入纯数字的Arcaea ID')
