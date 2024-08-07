from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, FriendMessage, At, MessageEvent
from mirai_extensions.trigger.message import GroupMessageFilter, FriendMessageFilter
from mirai_extensions.trigger import InterruptControl
from PIL import ImageDraw, ImageFont
from io import BytesIO
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np
import base64
import qianfan
import jieba
import glob
import sqlite3
import snownlp
from snownlp import SnowNLP
import threading
import urllib
from pathlib import Path
import math
from typing import Tuple
import pandas as pd
import logging
import random
import os
import io
import re
import colorlog
import time
import sys
import configparser
import requests
import string
import json
import asyncio
import inspect
import websockets
# import shutil

py_version = 'v1.51'

data_dir = './data/'
db_path = os.path.join(data_dir, 'qq.db3')
pd.StringDtype('pyarrow')

# RL快速方法正则式
WEIGHTED_CHOICE_PATTERN = re.compile(
    r'%(?P<name>[^%!]+)%'
    r'(?:(?P<R>R:(\d*\.?\d*))?'
    r'(?:(?P<sep1>,)?(?P<L>L:(\d+)))?)?'
    r'!'
)

face_del = r'\{face:\d+\}'

csv_path = './data/reply.csv'  # 替换为你的CSV文件路径
config = configparser.ConfigParser()
image_folder = '.\data\CG'
# 只是log
logger = logging.getLogger('LoveYou')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
fmt_string = '%(log_color)s[%(name)s][%(levelname)s]%(message)s'
# black red green yellow blue purple cyan 和 white
log_colors = {
    'DEBUG': 'white',
    'INFO': 'cyan',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'purple'
}
fmt = colorlog.ColoredFormatter(fmt_string, log_colors=log_colors)
stream_handler.setFormatter(fmt)
logger.addHandler(stream_handler)
logger.info(
    '''  
.____                                _____.___.               
|    |    _______  __ ____           \__  |   | ____  __ __   
|    |   /  _ \  \/ // __ \           /   |   |/  _ \|  |  \  
|    |__(  <_> )   /\  ___/           \____   (  <_> )  |  /  
|_______ \____/ \_/  \___  >__________/ ______|\____/|____/   
        \/               \/_____/_____|/                       
''')
logger.info('-by hlfzsi')
time.sleep(1)
logger.info('正在加载reply.csv')
try:
    df = pd.read_csv(csv_path, header=None, dtype=str,
                     usecols=range(5), encoding='utf-8')
    df.iloc[:, 4] = df.iloc[:, 4].fillna('1')
    logger.info('reply.csv已成功加载')
except:
    logger.error('未能成功读取reply.csv,请确认文件是否存在')
    logger.error('程序将在5秒后退出')
    time.sleep(5)
    sys.exit()
logger.info('检查数据库...')
# 检查data目录是否存在，如果不存在则创建
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 连接到SQLite数据库
conn = None
try:
    # 尝试连接数据库，如果文件不存在则会自动创建
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查表是否存在
    cursor.execute('''
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='qq_love';
    ''')
    table_exists = cursor.fetchone() is not None

    # 如果表不存在，则创建表
    if not table_exists:
        cursor.execute('''
            CREATE TABLE qq_love (
                QQ TEXT PRIMARY KEY,
                love INTEGER
            );
        ''')

    # 提交事务
    conn.commit()
finally:
    # 关闭数据库连接
    if conn:
        conn.close()
logger.info('数据库检查完成')
MAX_AGE = timedelta(minutes=10)  # 消息的有效时间为10分钟
previous_msgs = defaultdict(datetime)
groups_df = {}


def loadconfig():
    # 读取配置文件
    config_path = os.path.join(os.getcwd(), "config.ini")
    try:
        with open(config_path, "r", encoding='utf-8') as config_file:
            config.read_file(config_file)
            logger.info('正在加载config.ini')
    except FileNotFoundError:
        logger.error('无法加载config.ini，请检查文件是否存在或格式是否正确')
        time.sleep(5)
        sys.exit(1)
    # 获取配置项的值
    bot_qq = config.get('bot', 'bot_qq')
    verify_key = config.get('bot', 'verify_key')
    host = config.get('bot', 'host')
    port = config.get('bot', 'port')
    bot_name = config.get('others', 'bot_name')
    baseline = config.getint('random_CG', 'baseline')
    rate = config.getfloat('random_CG', 'rate')
    master = config.get('others', 'master')
    lv_enable = config.get('lv', 'enable')
    common_love = config.get('csv', 'common_love')
    a, b = (value.strip() for value in common_love.split(','))
    search_love = config.get('others', 'search_love_reply')
    ws = config.get('others', 'ws')
    react = config.get('ai', '@_react')
    ws_port = config.getint('others', 'ws_port')
    model = config.get('ai', 'model')
    role = config.get('ai', 'role')
    API_Key = config.get('ai', 'API_Key')
    Secret_Key = config.get('ai', 'Secret_Key')
    tank_enable = config.get('others', 'tank_enable')
    memory = config.get('ai', 'memory')
    if memory == 'True':
        memory = True
    else:
        memory = False
    logger.info('config.ini第一部分已成功加载')
    return bot_qq, verify_key, host, port, bot_name, baseline, rate, master, lv_enable, a, b, search_love, ws, react, ws_port, model, role, API_Key, Secret_Key, tank_enable, memory


bot_qq, verify_key, host, port, bot_name, baseline, rate, master, lv_enable, Ca, Cb, search_love_reply, ws, botreact, ws_port, model, role, API_Key, Secret_Key, tank_enable, memory = loadconfig()
# 初始化ai回复
if botreact != 'True' or model == 'qingyunke':
    del role, API_Key, Secret_Key
else:
    os.environ["QIANFAN_AK"] = API_Key
    os.environ["QIANFAN_SK"] = Secret_Key
logger.info('ai对话初始化完成')

# logger.debug(bot_qq+'\n'+verify_key+'\n'+host+'\n'+port+'\n'+bot_name+'\n'+master+'\n'+lv_enable)
df.iloc[:, 2] = df.iloc[:, 2].fillna(f'({Ca},{Cb})')
del Ca, Cb


def get_range(value):
    if La <= value < Lb:
        logger.debug('获得lv1')
        return 1
    elif Lc <= value < Ld:
        logger.debug('获得lv2')
        return 2
    elif Le <= value < Lf:
        logger.debug('获得lv3')
        return 3
    elif Lg <= value < Lh:
        logger.debug('获得lv4')
        return 4
    elif Li <= value < Lj:
        logger.debug('获得lv5')
        return 5
    else:
        logger.debug('未获得lv')
        return None  # 返回None表示不属于任何已知范围


def ws_get_range(qq):
    try:
        love = read_love(qq)
        try:
            lv = get_range(int(love))
        except:
            lv = -1
        if lv == None and love >= 0:
            lv = 6
        elif lv == None and love < 0:
            lv = 0
        return lv
    except:
        return 'Fail'


def loadconfig_part2():
    # 读取配置文件
    config_path = os.path.join(os.getcwd(), "config.ini")
    try:
        with open(config_path, "r", encoding='utf-8') as config_file:
            config.read_file(config_file)
            logger.info('正在加载config.ini')
    except FileNotFoundError:
        logger.error('无法加载config.ini，请检查文件是否存在或格式是否正确')
        time.sleep(5)
        sys.exit(1)
    logger.info('正在加载第二部分config.ini')
    lv1 = config.get('lv', 'lv1')
    a, b = (value.strip() for value in lv1.split(','))
    lv2 = config.get('lv', 'lv2')
    c, d = (value.strip() for value in lv2.split(','))
    lv3 = config.get('lv', 'lv3')
    e, f = (value.strip() for value in lv3.split(','))
    lv4 = config.get('lv', 'lv4')
    g, h = (value.strip() for value in lv4.split(','))
    lv5 = config.get('lv', 'lv5')
    i, j = (value.strip() for value in lv5.split(','))
    lv1_reply = config.get('lv', 'lv1_reply')
    lv1_reply = lv1_reply.replace('\\n', '\n')
    lv2_reply = config.get('lv', 'lv2_reply')
    lv2_reply = lv2_reply.replace('\\n', '\n')
    lv3_reply = config.get('lv', 'lv3_reply')
    lv3_reply = lv3_reply.replace('\\n', '\n')
    lv4_reply = config.get('lv', 'lv4_reply')
    lv4_reply = lv4_reply.replace('\\n', '\n')
    lv5_reply = config.get('lv', 'lv5_reply')
    lv5_reply = lv5_reply.replace('\\n', '\n')
    logger.info('config.ini第二部分已成功加载')
    return a, b, c, d, e, f, g, h, i, j, lv1_reply, lv2_reply, lv3_reply, lv4_reply, lv5_reply


if lv_enable == 'True':
    logger.info('初始化好感等级...')
    La, Lb, Lc, Ld, Le, Lf, Lg, Lh, Li, Lj, lv1_reply, lv2_reply, lv3_reply, lv4_reply, lv5_reply = loadconfig_part2()
    try:
        La = int(La)
        Lb = int(Lb)
        Lc = int(Lc)
        Ld = int(Ld)
        Le = int(Le)
        Lf = int(Lf)
        Lg = int(Lg)
        Lh = int(Lh)
        Li = int(Li)
        Lj = int(Lj)
        logger.info('好感等级加载完成')
    except:
        logger.error('好感等级条件填写有误,请填写整数')
        logger.error('程序将在5秒后退出')
        time.sleep(5)
        sys.exit
else:
    logger.info('好感等级无需加载')
    logger.info('config.ini第二部分已跳过加载')
    time.sleep(1)


try:
    response = requests.get(
        "https://api.github.com/repos/hlfzsi/yirimirai_LoveYou/releases/latest")
    py_update = (response.json()["tag_name"])
    if py_version == py_update:
        logger.info('当前已为最新版本'+py_version)
    elif 'beta' in py_version:
        logger.warning('当前为beta版,程序并不稳定')
        logger.warning(
            '前往https://github.com/hlfzsi/yirimirai_LoveYou/releases获得最新版')
    else:
        logger.warning('本项目有更新,请前往https://github.com/hlfzsi/yirimirai_LoveYou/releases\n' +
                       '当前版本:'+py_version+'  最新版本:'+py_update)
except:
    logger.warning('未连接到网络,无法检查更新')
del py_update
del py_version
time.sleep(3)

'''
def clear_group_not_exist(groupid:str)->None:
    #清理退出群聊文件
    shutil.rmtree(f'./data/group/{groupid}')
    shutil.rmtree(f'./data/pic/group/{groupid}')
    logger.debug(f'{groupid}文件已清理')
'''


def chat_memory(qq: str, question: str, answer: str):
    """处理用户对话

    如果answer为空,则只添加question并返回字符串.文件不保留.

    如果answer非空,无return,保留修改

    Args:
        qq (str): 用户
        question (str): 用户消息
        answer (str): 回复消息
    """
    # 构造文件路径
    file_path = os.path.join('./data/memory', f'{qq}.json')

    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 初始化聊天记录列表，如果文件不存在则为空列表
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            records = json.load(file)
    except:
        records = []

    # 如果answer不是空字符串，则添加新的聊天记录
    if answer:  # 检查answer是否为非空字符串
        records.append({"role": "user", "content": question})
        records.append({"role": "assistant", "content": answer})
        records_json = json.dumps(records, ensure_ascii=False, indent=4)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(records, file, ensure_ascii=False, indent=4)
        return None
    else:
        records.append({"role": "user", "content": question})
        records_json = json.dumps(records, ensure_ascii=False, indent=4)
        records_json = json.loads(records_json)
        return records_json


def clear_memory(qq: str):
    file_path = os.path.join('./data/memory', f'{qq}.json')
    try:
        os.remove(file_path)
    except:
        pass


def reduce_memory(qq: str):
    file_path = f"./data/memory/{qq}.json"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    del data[:2]
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


async def baidu_ai(msg: str, qq: str, intlove, name: str) -> str:
    '''
    通过百度模型获得ai回复
    '''
    intlove = str(intlove)
    time = datetime.now()
    time = time.strftime("%Y-%m-%d.%H:%M")
    loacl_role = role
    loacl_role = loacl_role.replace(
        '[intlove]', intlove).replace('[sender]', name).replace('[time]', time)
    if memory == True:
        send_msg = chat_memory(qq, msg, '')
        while len(send_msg) + len(loacl_role) >= 24000:
            reduce_memory(qq)
            send_msg = chat_memory(qq, msg, '')
        resp = qianfan.ChatCompletion().do(model=model,
                                           messages=send_msg, temperature=0.98, top_p=0.7, penalty_score=1, system=loacl_role)
        try:
            chat_memory(qq, msg, resp['result'])
            if resp['need_clear_history'] == True or resp['need_clear_history'] == 'True':
                clear_memory(qq)
                logger.debug('清理用户记忆')
        except:
            pass

    elif memory == False:
        resp = qianfan.ChatCompletion().do(model=model,
                                           messages=[{"role": "user", "content": msg}], temperature=0.98, top_p=0.7, penalty_score=1, system=loacl_role)

    try:
        return resp['result']
    except:
        return '模型填写错误喵~猫闹过载ing'


def choose_pic(qq, images_dir='./data/images/'):
    """
    从给定路径下取出以qq为文件名的图片（不论后缀如何），
    如果不存在，取出default.jpg。

    参数:
    qq (str): 文件名（不包括后缀）
    images_dir (str, optional): 图片所在的目录路径。

    返回:
    str: 匹配的图片文件路径或default.jpg的路径
    """
    # 将路径转换为Path对象，以便使用Path方法
    images_dir = Path(images_dir)

    # 遍历目录以查找匹配的文件
    for file in images_dir.iterdir():
        # 如果文件名（不包括后缀）与qq匹配
        if file.stem == qq:
            # 返回匹配的文件路径
            return str(file)

    # 如果没有找到匹配的文件，返回default.jpg的路径
    logger.warning('没有找到匹配的文件，返回default.jpg')
    return str(images_dir / 'default.jpg')


def pic_reply(qq, name, background_path, ico):
    """生成用户图片化的好感查询结果

    Args:
        qq (str): 用户qq号
        name (str): 群名片
        background_path (str): 用户底层背景
        ico (str): 用户头像

    Returns:
        bytes: 图片结果的base64编码
    """
    from PIL import Image
    int_love, str_love = get_both_love(qq)

    def sentence():
        ci = random.choice('abcdefghijkl')
        url = "https://v1.hitokoto.cn/?c=" + ci + "&encode=text"
        r = requests.post(url)
        return r.text
    sen = sentence()

    def part_cover(image):
        # 创建一个与原图大小相同的RGBA图片，用于存放结果
        result = image.copy().convert('RGBA')

    # 创建一个与蒙版大小相同的白色（带有50%透明度的）蒙版
        mask = Image.new('RGBA', (1000, 1000),
                         (255, 255, 255, 128))  # 128 = 50% 透明度

    # 将蒙版粘贴到结果图片的中心位置
        result.paste(mask, (12, 12, 1012, 1012), mask)

        return result

    def is_image_file(filename):
        # 判断一个文件名是否为图片文件
        return any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp'])

    def pick_pic(path, number):
        # 构造对应number的文件夹路径
        folder_path = os.path.join(path, str(number))
        # 获取文件夹中的所有文件和子目录
        files = os.listdir(folder_path)

        # 过滤出图片文件
        image_files = [os.path.join(folder_path, f)
                       for f in files if is_image_file(f)]

        # 如果没有图片文件，则返回一个错误消息
        if not image_files:
            logger.error('无对应贴画可供使用')

        # 随机选择一个图片文件
        chosen_image = random.choice(image_files)

        # 返回完整图片路径
        return chosen_image

    def add_cartoon(bg, cartoon):
        # 随机选择一个位置放置cartoon
        left = random.randint(0, 689)
        top = random.randint(0, 689)

        # 在bg图片上粘贴cartoon图片
        bg.paste(cartoon, (left, top), cartoon)

        # 返回结果图片
        return bg

    # 打开背景图片
    background = Image.open(background_path)
    background = background.resize((1024, 1024), Image.LANCZOS)
    lv = get_range(int_love)
    if lv == None and int_love > 0:
        lv = 5
        lv_r = 'Nan'
    elif lv == None and int_love <= 0:
        lv = 1
        lv_r = 'Nan'
    else:
        lv_r = str(lv)
    # 打开图标图片
    response = requests.get(ico)
    image_bytes = response.content
    ico = Image.open(BytesIO(image_bytes))
    cartoon = pick_pic('./data/images/cartoon/', lv)
    cartoon = Image.open(cartoon)
    # 缩放图标到325x325像素
    ico = ico.resize((325, 325), Image.LANCZOS)
    cartoon = cartoon.resize((335, 335), Image.LANCZOS)
    cartoon = cartoon.convert('RGBA')
    background = background.convert('RGBA')
    background.paste(ico, (590, 75))
    background = add_cartoon(background, cartoon)
    background = part_cover(background)
    draw = ImageDraw.Draw(background)

    # 加载字体
    font = ImageFont.truetype('arial.ttf', 60)
    font2 = ImageFont.truetype('arial.ttf', 75)
    draw.text((19, 100), name, font=font2, fill=(128, 118, 105))
    draw.text((19, 354), '好感等级:Lv.'+lv_r, font=font, fill=(244, 27, 90))
    draw.text((19, 508), '好感度:'+str_love, font=font, fill=(244, 27, 90))
    senl = sen.replace(',', '，').replace(
        '.', '。').replace('，', ',\n').replace('。', '。\n')
    draw.text((75, 662), senl, font=font, fill=(0, 0, 0))
    background = background.convert('RGB')
    buffered = io.BytesIO()
    background.save(buffered, format='JPEG')
    result = buffered.getvalue()
    result = base64.b64encode(result)
    return result


async def qingyunke(msg):
    url = 'http://api.qingyunke.com/api.php?key=free&appid=0&msg={}'.format(
        urllib.parse.quote(msg))
    html = requests.get(url)
    return html.json()["content"]


def del_admin(groupid, qq, filename='./data/admin.json'):
    admin_data = load_admin(filename)

    # 检查groupid和common列表是否存在
    if groupid in admin_data and 'common' in admin_data[groupid]:
        if qq in admin_data[groupid]['common']:
            # 尝试在common列表中删除qq
            admin_data[groupid]['common'].remove(qq)
            with open(filename, 'w') as file:
                json.dump(admin_data, file, indent=4)
        global admin_qqs
        admin_qqs = load_admin()


def del_admin_high(groupid, qq, filename='./data/admin.json'):
    admin_data = load_admin(filename)

    # 检查groupid和high列表是否存在
    if groupid in admin_data and 'high' in admin_data[groupid]:
        # 检查qq是否在high列表中
        if qq in admin_data[groupid]['high']:
            # 尝试在high列表中删除qq
            admin_data[groupid]['high'].remove(qq)
            with open(filename, 'w') as file:
                json.dump(admin_data, file, indent=4)
            global admin_qqs
            admin_qqs = load_admin()


def load_admin(filename='./data/admin.json'):
    try:
        with open(filename, 'r') as file:
            data = json.load(file, strict=False)
        return data
    except:
        return {}


admin_qqs = load_admin()


def write_admin(groupid, type_, qq, filename='./data/admin.json'):
    admin_data = load_admin(filename)

    # 检查groupid是否存在
    if groupid not in admin_data:
        # 如果不存在，则新建groupid，并初始化high和common列表
        admin_data[groupid] = {
            'high': [],
            'common': []
        }

    # 检查type_是否有效
    if type_ not in ['high', 'common']:
        raise ValueError("Invalid type. It should be 'high' or 'common'.")

    isAdmin = check_admin(groupid, qq)
    if isAdmin == type_:
        return None

    # 将qq添加到对应type_的列表中
    admin_data[groupid][type_].append(qq)

    # 将更新后的数据写回JSON文件
    with open(filename, 'w') as file:
        json.dump(admin_data, file, indent=4)
    global admin_qqs
    admin_qqs = load_admin()


def check_admin(groupid, qq):
    # 检查 groupid 是否存在于 admin_qqs 中
    if groupid in admin_qqs:
        # 检查 'high' 列表
        if qq in admin_qqs[groupid]['high']:
            return 'high'
        # 检查 'common' 列表
        elif qq in admin_qqs[groupid]['common']:
            return 'common'
    # 如果 qq 在所有的 groupid 下都没有找到，返回 False
    return False


def group_load(groupid):
    '''
    加载群聊词库

    这一函数通常可以被 global groups_df | groups_df[groupid] = df 完全取代

    请避免使用本函数,因为它的性能不如替代方案

    如果你需要加载所有词库,请使用read_csv_files_to_global_dict函数
    '''
    # 构造文件路径
    file_path = os.path.join('./data/group', f"{groupid}.csv")

    # 如果文件存在，读取CSV到DataFrame
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, dtype=str,
                         usecols=range(6), encoding='utf-8')
        # 将DataFrame添加到全局字典中，以groupid为键
        global groups_df
        groups_df[groupid] = df


def group_write(groupid: str, question: str, answer: str, type: str):
    '''
    groupid:群号
    question:触发词
    answer:回复
    type:类型.1为精准匹配,2为模糊匹配
    '''
    # 构造文件路径

    base_path = './data/group'
    file_path = os.path.join(base_path, f"{groupid}.csv")

    # 如果文件不存在，创建一个空的DataFrame
    if not os.path.exists(file_path):
        df = pd.DataFrame(
            columns=['Question', 'Answer', 'Love', 'Range', 'Type', 'Status'])
    else:
        global groups_df
        # 如果文件存在，读取它
        df = groups_df[groupid]

    # 将新的数据添加到DataFrame中
    new_row = pd.DataFrame([[question, answer, '', '', type, '']], columns=[
                           'Question', 'Answer', 'Love', 'Range', 'Type', 'Status'])
    df = pd.concat([df, new_row], ignore_index=True)

    # 将DataFrame写入CSV文件
    df.to_csv(file_path, index=False, encoding='utf-8')
    groups_df[groupid] = df
    # group_load(groupid)

    logger.debug('写入成功')


def group_del(groupid, question):
    # 构造文件路径
    file_path = os.path.join('./data/group', f"{groupid}.csv")
    global groups_df

    if groupid in groups_df:
        df = groups_df[groupid]

        # 找到与question完全匹配且Status不为locked的行
        mask = (df['Question'] == question) & (df['Status'] != 'locked')
        rows_to_delete = df[mask].index.tolist()

        # 从后向前删除行，避免索引变化影响迭代
        for index in sorted(rows_to_delete, reverse=True):
            row = df.iloc[index]
            if '[pic=' in row['Answer']:
                _, path = pic_support(row['Answer'])
                try:
                    os.remove(f'./data/pic/group/{groupid}/{path}')
                except FileNotFoundError:
                    logger.warning(f"文件 {path} 未找到，无法删除。")
            # 删除DataFrame中的行
            df.drop(index, inplace=True)

        # 将修改后的DataFrame写回CSV文件
        df.to_csv(file_path, index=False)

        # 更新全局变量
        groups_df[groupid] = df

        logger.debug('删除成功')
    else:
        logger.warning(f"{file_path}不存在")


def jaccard_similarity(list1, list2):
    intersection = len(set(list1).intersection(set(list2)))
    union = len(set(list1)) + len(set(list2)) - intersection
    return intersection / union if union else 0


def tokenize(text):
    return list(jieba.cut(text, cut_all=False))


def new_msg_judge(msg, jaccard_threshold=0.75):
    # 使用结巴库进行分词
    tokens = tokenize(msg)

    # 清理过期的消息
    current_time = datetime.now()
    for prev_msg, timestamp in list(previous_msgs.items()):
        if (current_time - timestamp) >= MAX_AGE:
            del previous_msgs[prev_msg]

    # 检查当前消息是否与先前的消息高度相似
    for prev_msg, timestamp in previous_msgs.items():
        prev_tokens = tokenize(prev_msg)
        jaccard_sim = jaccard_similarity(tokens, prev_tokens)
        if jaccard_sim >= jaccard_threshold:
            return False  # 如果找到高度相似的msg且在MAX_AGE内，返回False

    # 如果没有找到高度相似的msg，将其添加到previous_msgs字典中
    previous_msgs[msg] = datetime.now()
    return True


def map_sentiment_to_range(sentiment_score, target_min=-10, target_max=10):
    # 线性映射函数，但调整斜率使得中间区域变化小，极端值变化大
    if sentiment_score >= 0.54:
        # 正面情感，使用较缓的斜率
        mapped_score = (sentiment_score - 0.5) * 2 * (target_max -
                                                      target_min) + target_min + (target_max - target_min) / 2.41
    elif sentiment_score <= 0.46:
        mapped_score = (sentiment_score - 0.6) * 2 * (target_max -
                                                      target_min) + target_min + (target_max - target_min) / 2.41
    else:
        mapped_score = (sentiment_score - 0.5) * 2 * (target_max -
                                                      target_min) + target_min + (target_max - target_min) / 2.41

    # 确保值在目标范围内
    mapped_score = max(min(mapped_score, target_max), target_min)
    return mapped_score


def add_random_fluctuation(score, target_min, target_max):
    # 添加一个固定的随机波动在[-1, 1]范围内
    fluctuation = random.uniform(-1, 1)
    fluctuated_score = max(
        min(score + fluctuation, target_max), target_min)  # 确保值在目标范围内
    return fluctuated_score


def adjust_score_if_high(score, threshold, deduction_range):
    # 如果得分大于等于阈值，则随机减去一个整数
    if score >= threshold:
        deduction = random.randint(deduction_range[0], deduction_range[1])
        score -= deduction
        score = math.floor(score)
    return score


def adjust_score_if_low(score, threshold, deduction_range):
    # 如果得分小于等于阈值，则随机加上一个整数
    if score <= threshold:
        deduction = random.randint(deduction_range[0], deduction_range[1])
        score += deduction
        score = math.floor(score)
    return score


def love_score(text: str, target_min=-10, target_max=10):
    # 使用 SnowNLP 分析文本情感倾向
    s = snownlp.SnowNLP(text)
    sentiment_score = s.sentiments

    # 映射情感倾向
    mapped_score = map_sentiment_to_range(
        sentiment_score, target_min, target_max)

    # 添加随机波动
    fluctuated_score = add_random_fluctuation(
        mapped_score, target_min, target_max)
    fluctuated_score = adjust_score_if_high(fluctuated_score, 7, [0, 7])
    final_score = adjust_score_if_low(fluctuated_score, -7, [0, 7])
    final_score = int(final_score)

    # 返回结果
    return final_score


def generate_codes(a, b):
    '''a为数目,b为类型'''
    if b == 0:
        filename = './data/alias_code.txt'
    elif b == 1:
        filename = './data/love_code.txt'
    elif b == 2:
        filename = './data/pic_code.txt'
    # 字符集，包含大小写字母和数字
    characters = string.ascii_letters + string.digits

    # 读取文件中的所有code并放入集合中
    with open(filename, 'r', encoding='utf-8') as file:
        existing_codes = set(line.strip() for line in file if line.strip())

    # 初始生成的code集合
    generated_codes = set()

    # 生成code的循环
    while len(generated_codes) < a:
        # 一次性生成多个code以提高效率
        batch_size = 1  # 可以根据实际情况调整
        new_codes = set(
            ''.join(random.choices(characters, k=8)) for _ in range(batch_size)
        )

        # 使用集合的差集操作来获取不与现有code重复的code
        unique_codes = new_codes - existing_codes

        # 更新生成的code集合和已存在的code集合
        generated_codes.update(unique_codes)
        existing_codes.update(unique_codes)

    # 将生成的code写入文件
    with open(filename, 'w', encoding='utf-8') as file:
        for code in generated_codes:
            file.write(code + '\n')


def write_str_love(qq, str_value, file_path='.\data\qq.txt'):
    with open(file_path, 'r+', encoding='utf-8') as file:
        lines = file.readlines()
        updated = False
        new_lines = []
        for line in lines:
            line = line.strip()  # 移除行尾的换行符和可能的空白字符
            if line.startswith(qq + '='):
                # 如果找到匹配的qq，则更新它并标记为已更新
                new_lines.append(f"{qq}={str_value}\n")
                updated = True
            else:
                # 否则保留原行
                new_lines.append(line + '\n')

        # 如果qq不存在于文件中，则添加新行
        if not updated:
            new_lines.append(f"{qq}={str_value}\n")

        # 回到文件开头并写入所有行
        file.seek(0)
        file.writelines(new_lines)
        file.truncate()  # 确保文件大小正确


def write_pic(qq, pic, file_path='.\data\pic.txt'):
    with open(file_path, 'r+', encoding='utf-8') as file:
        lines = file.readlines()
        updated = False
        new_lines = []
        for line in lines:
            line = line.strip()  # 移除行尾的换行符和可能的空白字符
            if line.startswith(qq + '='):
                # 如果找到匹配的qq，则更新它并标记为已更新
                new_lines.append(f"{qq}={pic}\n")
                updated = True
            else:
                # 否则保留原行
                new_lines.append(line + '\n')

        # 如果qq不存在于文件中，则添加新行
        if not updated:
            new_lines.append(f"{qq}={pic}\n")

        # 回到文件开头并写入所有行
        file.seek(0)
        file.writelines(new_lines)
        file.truncate()  # 确保文件大小正确


def code_record(a):
    # 获取当前时间，并格式化为字符串（精确到秒）
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 构建要写入文件的字符串，包括时间和传入的字符串a
    message = f"{current_time} - {a}\n"

    # 打开文件以追加模式（'a'），将内容追加到文件末尾
    with open('./data/code_users.txt', 'a', encoding='utf-8') as file:
        file.write(message)


def RL_support(s: str) -> Tuple[str, int]:
    items = []
    total_weight = 0.0

    # 解析字符串并构建items列表
    for match in WEIGHTED_CHOICE_PATTERN.finditer(s):
        item = {
            'name': match.group('name'),
            # R值，默认1.0
            'R': float(match.group('R')[2:] if match.group('R') else '1.0'),
            # L值，默认0
            'L': int(match.group('L')[2:] if match.group('L') else '0')
        }
        total_weight += item['R']
        items.append(item)

    # 如果没有有效的items，返回默认值
    if not items:
        return '', 0

    # 按照权重随机选择
    r = random.random() * total_weight
    for item in items:
        r -= item['R']
        if r <= 0:
            return item['name'], item['L']
    logger.warning('RL出现异常')
    return None, 0  # 或者考虑抛出一个异常


def pic_support(text: str) -> Tuple[str, str]:
    '''返回图片名称'''
    # 正则表达式匹配 [pic=任意图片名.(png|jpg|jpeg)]
    pattern = r'\[pic=(.*?\.(png|jpg|jpeg))\]'

    # 查找所有匹配项
    matches = re.findall(pattern, text)

    # 如果没有找到匹配项，则直接返回原字符串和 None
    if not matches:
        return text, None

    # 只关心第一个匹配项
    path = matches[0][0]

    # 使用 re.sub() 替换掉第一个匹配项
    new_text = re.sub(pattern, '', text, count=1)

    return new_text, path


def update_alias(qq, str_value, alias_file='./data/alias.txt'):
    with open(alias_file, 'r+', encoding='utf-8') as file:
        lines = file.readlines()
        updated = False
        new_lines = []
        for line in lines:
            line = line.strip()  # 移除行尾的换行符和可能的空白字符
            if line.startswith(qq + '='):
                # 如果找到匹配的qq，则更新它并标记为已更新
                new_lines.append(f"{qq}={str_value}\n")
                updated = True
            else:
                # 否则保留原行
                new_lines.append(line + '\n')

        # 如果qq不存在于文件中，则添加新行
        if not updated:
            new_lines.append(f"{qq}={str_value}\n")

        # 回到文件开头并写入所有行
        file.seek(0)
        file.writelines(new_lines)
        file.truncate()  # 确保文件大小正确
        global alias_dict
        alias_dict = read_alias()


def read_alias(alias_file='./data/alias.txt'):
    alias_dict = {}
    try:
        with open(alias_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if '=' in line:
                    parts = line.split('=')
                    if len(parts) == 2:
                        qq, str_value = parts
                        alias_dict[qq] = str_value
    except FileNotFoundError:
        logger.error(f"文件 {alias_file} 不存在.")
    return alias_dict


alias_dict = read_alias()


def current_timestamp():
    return int(time.time())

# 写入或更新用户的最后判断时间戳


def update_user_timestamp(user_id, timestamp):
    with open('./data/recorder.txt', 'a+') as f:
        # 定位到用户ID的部分（如果存在）
        f.seek(0)
        lines = f.readlines()
        updated = False

        # 遍历行并更新或添加用户的时间戳
        new_lines = []
        for line in lines:
            if line.startswith(str(user_id) + '='):
                # 更新时间戳
                new_lines.append(f"\n{user_id}={timestamp}")
                updated = True
                break
            else:
                new_lines.append(line)

        # 如果用户的时间戳不存在，则添加
        if not updated:
            new_lines.append(f"\n{user_id}={timestamp}")

        # 回写文件
        f.seek(0)
        f.truncate(0)
        f.writelines(new_lines)
        logger.debug('时间戳回写')

# 读取用户的最后判断时间戳


def get_user_timestamp(user_id):
    try:
        with open('./data/recorder.txt', 'r') as f:
            for line in f:
                if line.startswith(str(user_id) + '='):
                    return int(line.split('=')[1].strip())
                logger.debug('时间戳读取完成')
        return None
    except FileNotFoundError:
        logger.warning('./data/recorder.txt丢失')
        return None


def replace_alias(text):
    for qq, str_value in alias_dict.items():
        pattern = rf'{re.escape(qq)}'
        text = re.sub(pattern, str_value, text)
    return text


def read_codes(filename='./data/alias_code.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            codes = file.read().splitlines()
        return codes
    except FileNotFoundError:
        print(f"文件 {filename} 未找到。")
        return []


def write_codes(codes, filename='./data/alias_code.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for code in codes:
            file.write(code + '\n')


def check_alias_code(code_to_check, filename='./data/alias_code.txt'):
    codes = read_codes(filename)
    if code_to_check in codes:
        codes.remove(code_to_check)
        write_codes(codes, filename)
        return True
    return False


def read_codes_love(filename='./data/love_code.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            codes = file.read().splitlines()
        return codes
    except FileNotFoundError:
        print(f"文件 {filename} 未找到。")
        return []


def write_codes_love(codes, filename='./data/love_code.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for code in codes:
            file.write(code + '\n')


def check_love_code(code_to_check, filename='./data/love_code.txt'):
    codes = read_codes_love(filename)
    if code_to_check in codes:
        codes.remove(code_to_check)
        write_codes_love(codes, filename)
        return True
    return False


def read_codes_pic(filename='./data/pic_code.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            codes = file.read().splitlines()
        return codes
    except FileNotFoundError:
        print(f"文件 {filename} 未找到。")
        return []


def write_codes_pic(codes, filename='./data/pic_code.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for code in codes:
            file.write(code + '\n')


def check_pic_code(code_to_check, filename='./data/pic_code.txt'):
    codes = read_codes_pic(filename)
    if code_to_check in codes:
        codes.remove(code_to_check)
        write_codes_pic(codes, filename)
        return True
    return False


def updata_love(qq: str, love: int):
    """更新用户好感

    Args:
        qq (str)
        love (int): 好感变化量
    """
    # 连接到SQLite数据库
    with sqlite3.connect(db_path) as conn:
        # 创建一个游标对象
        cursor = conn.cursor()

        # 构造一个SQL语句，用于查找并更新
        update_sql = "UPDATE qq_love SET love = love + ? WHERE QQ = ?"

        # 尝试执行更新操作
        cursor.execute(update_sql, (love, qq))

        # 如果没有匹配的行被更新（即没有找到匹配的QQ），则插入新记录
        if cursor.rowcount == 0:
            insert_sql = "INSERT INTO qq_love (QQ, love) VALUES (?, ?)"
            cursor.execute(insert_sql, (qq, love))

        # 提交事务
        conn.commit()


def ws_change_love(qq, love):
    '''
    只用于ws,一般不需要在程序中使用
    '''
    try:
        qq = str(qq)
        love = int(love)
        updata_love(qq, love)
        return 'DONE'
    except:
        return 'Fail'


def ws_load_love(qq):
    '''
    只用于ws,一般不需要在程序中使用
    '''
    try:
        qq = str(qq)
        int_love, str_love = get_both_love_obly(qq)
        if int_love != None:
            return str(int_love)+'|||' + str_love
        else:
            return 'None'
    except:
        return 'Fail'


def get_global_reply(search_term: str, m: int) -> Tuple[str, int]:
    """检查词库获得回复

    Args:
        search_term (str): 需要匹配的内容
        m (int): 用户的数值好感度
    Returns:
        Tuple[str,int]: 回复,好感变化值
    """
    # 筛选匹配第一列的行
    matches = df[(df.iloc[:, 4] == '1') & (df.iloc[:, 0] == search_term)]
    if matches.empty:         # 如果没有找到匹配的行，进行模糊匹配
        if len(search_term) <= 90:
            # 使用列表推导式来检查search_term是否包含第一列中的任何字符串
            condition = [str(x) in search_term for x in df.iloc[:, 0]]
            condition = pd.Series(condition, index=df.index)
            matches = df[(df.iloc[:, 4] == '2') &
                         condition]

        else:
            return None, None
   # 模糊匹配无法高效率实现，因此在全局词库中考虑抛弃该功能

    # 过滤掉第四列(c, d)范围不包含m的行，并处理空值
    def is_m_in_range(row):
        cd_str = str(row.iloc[3])
        if cd_str.strip() == "nan" or cd_str.strip() == "":  # 如果为空值或空字符串，则认为m符合范围
            return True
        try:
            c, d = map(int, cd_str.strip('()').split(','))
            return c <= m <= d  # 检查 m 是否在 (c, d) 范围内
        except ValueError:  # 如果无法转换为整数
            return True

    valid_matches = matches.apply(is_m_in_range, axis=1)
    valid_matches = matches[valid_matches]

    # 如果没有找到匹配的行
    if valid_matches.empty:
        return None, None

    # 从有效匹配中随机选择一行
    chosen_row = valid_matches.sample(n=1).iloc[0]

    # 读取第二列作为reply，如果为空则跳过
    reply = chosen_row.iloc[1] if pd.notnull(chosen_row.iloc[1]) else None

    # 读取第三列(a, b)范围，并在范围内随机选择一个整数作为love，处理空值
    ab_str = str(chosen_row.iloc[2])
    if ab_str.strip() == "":  # 如果为空字符串
        love = 0
    else:
        try:
            a, b = map(int, ab_str.strip('()').split(','))
            love = random.randint(a, b)
        except ValueError:
            love = 0
    logger.debug('完成回复配对')
    return reply, love


def groups_reply(groupid, search_term, m):
    """检查词库获得回复

    Args:
        groupid(str):用户对应的群号,用于选择词库
        search_term (str): 需要匹配的内容
        m (int): 用户的数值好感度

    Returns:
        Tuple[str,int]: 回复,好感变化值
    """
    global groups_df
    if groupid in groups_df:
        df = groups_df[groupid]
        # df.iloc[:, 4] = df.iloc[:, 4].fillna('1')
        # 筛选匹配第一列的行
        matches = df[(df.iloc[:, 4] == '1') & (df.iloc[:, 0] == search_term)]
        if matches.empty:         # 如果没有找到匹配的行，进行模糊匹配
            if len(search_term) <= 90:
                # 使用列表推导式来检查search_term是否包含第一列中的任何字符串
                condition = [str(x) in search_term for x in df['Question']]
                condition = pd.Series(condition, index=df.index)
                matches = df[(df['Type'] == '2') &
                             condition]

            else:
                return None, 0

        # 过滤掉第四列(c, d)范围不包含m的行，并处理空值
        def is_m_in_range(row):
            cd_str = str(row.iloc[3])
            if cd_str.strip() == "nan" or cd_str.strip() == "":  # 如果为空值或空字符串，则认为m符合范围
                return True
            try:
                c, d = map(int, cd_str.strip('()').split(','))
                return c <= m <= d  # 检查 m 是否在 (c, d) 范围内
            except ValueError:  # 如果无法转换为整数
                return True

        # 假设 matches 是一个pandas DataFrame，且第四列是字符串形式的范围，如"(1, 5)"
        # 或者第四列可能包含空值或无法转换为整数的字符串
        valid_matches = matches.apply(is_m_in_range, axis=1)
        valid_matches = matches[valid_matches]
        if valid_matches.empty:
            return None, None

        if valid_matches.empty:
            return None, None

        # 从有效匹配中随机选择一行
        chosen_row = valid_matches.sample(n=1).iloc[0]

        # 读取第二列作为reply，如果为空则跳过
        reply = chosen_row.iloc[1] if pd.notnull(chosen_row.iloc[1]) else None

        # 读取第三列(a, b)范围，并在范围内随机选择一个整数作为love，处理空值
        ab_str = str(chosen_row.iloc[2])
        if ab_str.strip() == "":  # 如果为空字符串
            love = 0
        else:
            try:
                a, b = map(int, ab_str.strip('()').split(','))
                love = random.randint(a, b)
            except ValueError:  # 如果无法转换为整数
                love = 0
        logger.debug('完成群聊回复配对')
        return reply, love
    else:
        return None, 0


qq_dict = {}


def generate_random_string(length=16):
    """  
    生成指定长度的包含大小写字母和数字的随机字符串  
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


def read_qq_txt_to_dict(file_path='./data/qq.txt'):
    # 创建一个空字典来存储键值对
    global qq_dict
    with open(file_path, 'r', encoding="utf-8") as file:
        # 逐行读取文件
        for line in file:
            # 去除行尾的换行符
            line = line.strip('')

            # 如果行不为空
            if line:
                # 尝试使用'='来分割键和值
                key_value = line.split('=', 1)  # 使用1来确保只分割一次

                # 检查是否成功分割
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = key_value[1].strip()

                    # 将键值对添加到字典中
                    # 如果键已存在，此操作将覆盖原有值
                    qq_dict[key] = value


read_qq_txt_to_dict()
pic_dict = {}


def read_pic_to_dict(file_path='./data/pic.txt'):
    # 创建一个空字典来存储键值对
    global pic_dict
    with open(file_path, 'r', encoding="utf-8") as file:
        # 逐行读取文件
        for line in file:
            # 去除行尾的换行符
            line = line.strip('')

            # 如果行不为空
            if line:
                # 尝试使用'='来分割键和值
                key_value = line.split('=', 1)  # 使用1来确保只分割一次

                # 检查是否成功分割
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = key_value[1].strip()

                    # 将键值对添加到字典中
                    # 如果键已存在，此操作将覆盖原有值
                    pic_dict[key] = value


read_pic_to_dict()


def read_love(qq):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # 尝试查询记录
        cursor.execute("SELECT love FROM qq_love WHERE QQ=?", (qq,))
        result = cursor.fetchone()

        # 如果记录存在，返回love的值
        if result:
            return result[0]
        else:
            # 如果记录不存在，插入新记录
            cursor.execute(
                "INSERT INTO qq_love (QQ, love) VALUES (?, 0)", (qq,))
            # 提交事务
            conn.commit()
            # 新增后默认返回0
            return 0


def get_loverank(qq: str) -> Tuple[str, str]:
    '''返回用户好感排名与整张表记录数'''
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM qq_love")
        total_records = cursor.fetchone()[0]

        cursor.execute("""  
            SELECT RANK() OVER (ORDER BY love DESC) AS rn  
            FROM qq_love  
            WHERE QQ = ?  
        """, (qq,))
        rank_result = cursor.fetchone()

        if rank_result:
            rank = rank_result[0]
            return str(rank), str(total_records)
        else:
            return 'Unfound', str(total_records)


def ws_get_rank(qq):
    try:
        rank, total = get_loverank(str(qq))
        return f"{rank}|{total}"
    except:
        return "Fail"


def read_love_only(qq):
    # 使用with语句确保连接在函数结束时被关闭
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # 尝试查询记录
        cursor.execute("SELECT love FROM qq_love WHERE QQ=?", (qq,))
        result = cursor.fetchone()

        # 如果记录存在，返回love的值
        if result:
            return result[0]
        else:
            return None


def get_both_love_obly(qq):
    """与get_both_love函数的唯一区别在于这个函数是只读的,不会插入记录
    """
    # 初始化返回值
    love = read_love_only(qq)
    if love != None:
        int_love = 0
        str_love = ''

        # 检查qq是否在字典中
        if qq in qq_dict:
            # 如果qq在字典中，则将字典中对应的文本加在love后
            str_love = str(love) + ' '+qq_dict[qq]
        else:
            # 如果qq不在字典中，则只将love转换为str类型
            str_love = str(love)

        # 无论如何，都将love赋值给int_love
        int_love = love

        # 返回两个值
        return int_love, str_love
    else:
        return None, None


def get_both_love(qq: str) -> Tuple[int, str]:
    """获得好感度,如果qq不存在则插入记录

    Args:
        qq (str):用户qq号

    Returns:
        数值好感(int),文本好感(str)
    """
    # 初始化返回值
    love = read_love(qq)
    int_love = 0
    str_love = ''

    # 检查qq是否在字典中
    if qq in qq_dict:
        # 如果qq在字典中，则将字典中对应的文本加在love后
        str_love = str(love) + ' ' + qq_dict[qq]
    else:
        # 如果qq不在字典中，则只将love转换为str类型
        str_love = str(love)

    # 无论如何，都将love赋值给int_love
    int_love = love

    # 返回两个值
    return int_love, str_love


def read_csv_files_to_global_dict(directory='./data/group'):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        # 检查文件是否为CSV文件
        if filename.endswith('.csv'):
            # 去除后缀以获取groupid
            groupid = os.path.splitext(filename)[0]
            # 构造文件路径
            file_path = os.path.join(directory, filename)
            # 读取CSV文件到DataFrame
            df = pd.read_csv(file_path, dtype=str,
                             usecols=range(6), encoding='utf-8')
            df.iloc[:, 4] = df.iloc[:, 4].fillna('1')
            # 将DataFrame添加到全局字典中，以groupid为键
            groups_df[groupid] = df


read_csv_files_to_global_dict()


def check_group_folder(groupid: str) -> str:
    '''返回文件夹路径'''
    folder_path = os.path.join('.\data\pic\group', groupid)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return f'{folder_path}\\'


def GlobalCompare():
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 编写SQL查询语句
        sql = "SELECT QQ FROM qq_love ORDER BY love DESC LIMIT 10"

        # 执行SQL查询
        cursor.execute(sql)

        # 获取查询结果
        qq_list = [row[0] for row in cursor.fetchall()]

        # 返回结果列表
        return qq_list
    except sqlite3.Error as e:
        # 如果出现错误，打印错误信息并返回空列表
        print(f"An error occurred: {e.args[0]}")
        return []
    finally:
        # 确保游标和连接都被关闭
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_low_ten_qqs():
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 执行 SQL 查询语句
    query = "SELECT qq FROM qq_love ORDER BY love ASC LIMIT 10"
    cursor.execute(query)

    # 获取查询结果，并转换为列表
    top_ten_qqs = [row[0] for row in cursor.fetchall()]

    # 关闭数据库连接
    conn.close()

    # 返回结果列表
    return top_ten_qqs


def find_row(groupid: str, question: str) -> list:
    # 从字典中获取DataFrame
    if groupid in groups_df:
        df = groups_df[groupid]
        # 使用列名Question来找到所有匹配的行
        matches = df[df['Question'] == question]
        # 如果找到了匹配的行，返回行号和Answer列的字符串列表
        if not matches.empty:
            # 使用matches.index来获取原始行号，并与Answer值一起构造列表
            logger.debug(f'完成在{groupid}的查找')
            return [f"{idx} : {matches.loc[idx, 'Answer']}" for idx in matches.index]
        else:
            logger.debug(f'完成在{groupid}的查找,但为空')
            return []  # 如果没有找到匹配的行，返回一个空列表
    else:
        logger.warning(f'{groupid}不在词库中')
        return ['当前词库不存在']


def del_row(groupid: str, row_indices: list):
    global groups_df
    if groupid in groups_df:
        # 构造文件路径
        base_path = './data/group'
        file_path = os.path.join(base_path, f"{groupid}.csv")

        df = groups_df[groupid]

        status_column = df['Status']
        column_with_images = df['Answer']

        # 过滤出row_indices中对应的且不是'locked'的行索引
        rows_to_update = [
            idx for idx in row_indices if idx in df.index and not status_column.iloc[idx] == 'locked']

        for idx in rows_to_update:
            if idx in df.index:
                status = status_column.iloc[idx]
                if not status == 'locked':
                    # 检查图片链接列是否包含'[pic='
                    if '[pic=' in str(column_with_images.iloc[idx]):
                        _, path = pic_support(
                            str(column_with_images.iloc[idx]))
                        os.remove(f'./data/pic/group/{groupid}/{path}')

        # 设置这些行为NaN
        df.loc[rows_to_update] = np.nan

        # 删除所有列都为NaN的行
        df.dropna(how='all', inplace=True)

        # 将修改后的DataFrame保存回文件
        df.to_csv(file_path, index=False)

        # 重新加载DataFrame到groups_df字典
        # group_load(groupid)
        groups_df[groupid] = df

        logger.debug(f'完成在{groupid}的行删除')
        return len(rows_to_update), len(row_indices) - len(rows_to_update)
    else:
        logger.warning(f'{groupid}不在词库中')
        return 0, 0


def lock_row(groupid: str, rows: list[str], type: int) -> None:
    # 从字典中获取DataFrame
    global groups_df
    if groupid in groups_df:
        df = groups_df[groupid]

        # 遍历字符串列表并尝试锁定相应的行
        for row_str in rows:

            # 尝试将字符串转换为整数
            row_int = int(row_str)
            # 检查行号是否有效
            if 0 <= row_int < len(df):
                # 锁定指定行的第六列（使用iloc和整数索引）
                if type == 0:
                    df.iloc[row_int, 5] = 'locked'
                elif type == 1:
                    df.iloc[row_int, 5] = 'unlocked'
            else:
                raise Exception
        # 构造文件路径
        base_path = './data/group'
        file_path = os.path.join(base_path, f"{groupid}.csv")

        # 将修改后的DataFrame保存回文件
        df.to_csv(file_path, index=False)

        # 重新加载DataFrame到groups_df字典
        # group_load(groupid)
        groups_df[groupid] = df
        logger.debug(f'完成在{groupid}的锁定修改')

    else:
        logger.warning(f'{groupid}不在词库中')
        raise Exception


def load_info(groupid: str, row: int) -> list:
    """获得指定行的详细信息

    Args:
        groupid (str): 群号
        row (int): 行数

    Returns:
        list|None: 正常情况下返回按列排序的list
    """
    global groups_df
    if groupid in groups_df:
        df = groups_df[groupid]
        if 0 <= row < len(df):  # 确保行号在DataFrame的行数范围内
            # 读取指定行的所有列内容
            row_data = df.iloc[row].fillna('None').tolist()    # 使用iloc通过整数位置索引
            logger.debug(f'完成在{groupid}的行查找')
            return row_data
        else:
            return None
    else:
        logger.warning(f'{groupid}不在词库中')
        return None


def hidden_pic(out_pic: str, hidden_pic: str, type: int) -> str:
    """制作幻影坦克

    Args:
        out_pic (url): 表图
        hidden_pic (url): 里图
        type (int): 0为黑白幻影坦克,1为彩色幻影坦克(当前彩坦因效果不理想暂不添加)

    Returns:
        str(base64): 幻影坦克图片
    """
    from PIL import Image

    def get_pic(url):
        response = requests.get(url)
        image_bytes = response.content
        pic = Image.open(BytesIO(image_bytes))
        return pic

    image_f = get_pic(out_pic)
    image_b = get_pic(hidden_pic)
    if type == 0:  # 黑白图像
        # 提取宽度和高度信息
        w_f, h_f = image_f.size
        w_b, h_b = image_b.size

        # 确定最小宽度和高度
        w_min = min(w_f, w_b)
        h_min = min(h_f, h_b)

        # 创建一个新的RGBA图像
        new_image = Image.new('RGBA', (w_min, h_min))

        # 将图片转换为灰度图
        image_f = image_f.convert('L')
        image_b = image_b.convert('L')

        # 加载像素数据到数组中
        array_f = image_f.load()
        array_b = image_b.load()

        # 计算缩放因子
        scale_h_f = h_f / h_min
        scale_w_f = w_f / w_min
        scale_h_b = h_b / h_min
        scale_w_b = w_b / w_min

        # 确定参考缩放比例
        scale_f = min(scale_h_f, scale_w_f)
        scale_b = min(scale_h_b, scale_w_b)

        # 计算平移值
        trans_f_x = (w_f - w_min * scale_f) / 2
        trans_b_x = (w_b - w_min * scale_b) / 2

        # 设置校正参数
        a = 10
        b = 6

        # 创建一个新的图像缓冲区来存储像素数据
        buffer = io.BytesIO()

        # 遍历新图像中的每个像素
        for i in range(w_min):
            for j in range(h_min):
                # 计算调整后的像素坐标
                mean_f = array_f[int(trans_f_x + i * scale_f),
                                 int(j * scale_f)]
                mean_b = array_b[int(trans_b_x + i * scale_b),
                                 int(j * scale_b)]

        # 计算新的像素值
                mean_f = mean_f * a / 10
                mean_b = mean_b * b / 10

                A_new = int(255 - mean_f + mean_b)

                if A_new == 0:
                    mean_new = 0
                elif A_new >= 255:
                    A_new = 255
                    mean_new = int((255 * mean_b) / A_new)
                else:
                    mean_new = int((255 * mean_b) / A_new)

                pixel_new = (mean_new, mean_new, mean_new, A_new)

        # 将像素放入新图像中
                new_image.putpixel((i, j), pixel_new)

        # 将新图像保存为base64编码的PNG格式
        buffered = io.BytesIO()
        new_image.save(buffered, format='PNG')
        encoded_image = buffered.getvalue()
        encoded_image = base64.b64encode(encoded_image)
        return encoded_image
    # elif type==1:      #彩色图像，效果不好
    # 技术尚不成熟，暂不添加


def isSilence(qq):
    try:
        global silence
        if qq == True or qq == "True":
            silence = True
            return 'Success'
        else:
            silence = False
            return 'Success'
    except:
        return 'Fail'


def mark_achieve():
    '''用于标记已经处理的事件'''
    global isAchieve
    isAchieve = True


if __name__ == '__main__':
    bot = Mirai(
        qq=bot_qq,  # 改成你的机器人的 QQ 号
        adapter=WebSocketAdapter(
            verify_key=verify_key, host=host, port=port
        )
    )
inc = InterruptControl(bot)

isAchieve = False  # 信号
silence = False  # 词库沉默


@bot.on(MessageEvent, priority=0)
def reset_isAchieve(event: MessageEvent):
    global isAchieve
    isAchieve = False


@bot.on(GroupMessage, priority=2)
async def bhrkhrt(event: GroupMessage):  # 词库功能实现
    message = str(event.message_chain)
    # if message.startswith('/') or message.startswith('.') or message.startswith('*') or message.startswith('-') or message.startswith('查询 ') or message.startswith('模糊问 ') or message.startswith('精确问 ') or message.startswith('删除 '):
    #    return None
    if isAchieve == True or silence == True:
        return None
    qq = str(event.sender.id)
    if qq == bot_qq:
        return None
    int_love, str_love = get_both_love(qq)
    name = event.sender.get_name()
    message = message.replace(qq, '[qq]').replace(name, '[sender]').replace(str(
        int_love), '[intlove]').replace(str_love, '[love]').replace(bot_name, '[bot]').replace('\n', '\\n')
    reply, love = get_global_reply(message, int_love)
    try:
        if reply == None:
            raise Exception
        reply = str(reply)

        if reply.startswith('RL'):  # RL快速方法
            # reply = reply.replace('RL', '')
            reply, love = RL_support(reply)
            logger.debug('RL '+reply)
        if '[pos]' in reply:
            s = snownlp.SnowNLP(message)
            sentiment_score = s.sentiments
            if sentiment_score <= 0.75:
                logger.debug('拒绝发送')
                return None
            else:
                reply = reply.replace('[pos]', '')
        if '[nag]' in reply:
            s = snownlp.SnowNLP(message)
            sentiment_score = s.sentiments
            if sentiment_score >= 0.25:
                logger.debug('拒绝发送')
                return None
            else:
                reply = reply.replace('[nag]', '')

        try:
            love = int(love)
        except:
            love = int(0)

        if '[cut]' in reply:
            reply_list = reply.split('[cut]')
            for i in reply_list:
                i = i.replace('[qq]', qq).replace('[sender]', name).replace('[intlove]', str(int_love)).replace(
                    '[love]', str_love).replace('[bot]', bot_name).replace('[vary]', str(love)).replace('\\n', '\n')
                i = replace_alias(i)
                i, pic = pic_support(i)
                logger.debug('cut '+i+'\n'+pic)
                if pic != None:
                    await bot.send(event, [i, Image(path='.\data\pic\\'+pic)])
                else:
                    await bot.send(event, i)
                time.sleep(1)

        else:
            reply = reply.replace('[qq]', qq).replace('[sender]', name).replace('[intlove]', str(int_love)).replace(
                '[love]', str_love).replace('[bot]', bot_name).replace('[vary]', str(love)).replace('\\n', '\n')
            reply = replace_alias(reply)
            reply, pic = pic_support(reply)
            if pic != None:
                await bot.send(event, [reply, Image(path='.\data\pic\\'+pic)])
            else:
                await bot.send(event, reply)
            if love != 0 and love != None:
                updata_love(qq, love)
                logger.debug('已更新用户好感')
        mark_achieve()
        return None
    except:
        pass

    if reply == None:  # 群聊词库支持
        groupid = str(event.sender.group.id)
        reply, love = groups_reply(groupid, message, int_love)
        try:
            if reply == None:
                raise Exception
            reply = str(reply)
            if reply.startswith('RL'):  # RL快速方法
                # reply = reply.replace('RL', '')
                reply, love = RL_support(reply)
                love = 0
                logger.debug('RL '+reply)
            if '[pos]' in reply:
                s = snownlp.SnowNLP(message)
                sentiment_score = s.sentiments
                if sentiment_score <= 0.75:
                    logger.debug('拒绝发送')
                    return None
                else:
                    reply = reply.replace('[pos]', '')
            if '[nag]' in reply:
                s = snownlp.SnowNLP(message)
                sentiment_score = s.sentiments
                if sentiment_score >= 0.25:
                    logger.debug('拒绝发送')
                    return None
                else:
                    reply = reply.replace('[nag]', '')

            try:
                love = int(love)
            except:
                love = int(0)

            if '[cut]' in reply:
                reply_list = reply.split('[cut]')
                for i in reply_list:
                    i = i.replace('[qq]', qq).replace('[sender]', name).replace('[intlove]', str(int_love)).replace(
                        '[love]', str_love).replace('[bot]', bot_name).replace('[vary]', str(love)).replace('\\n', '\n')
                    i = replace_alias(i)
                    i, pic = pic_support(i)
                    logger.debug('cut '+i+'\n'+pic)
                    if pic != None:
                        await bot.send(event, [i, Image(path='.\data\pic\group\\'+groupid+'\\'+pic)])
                    else:
                        await bot.send(event, i)
                time.sleep(1)

            elif reply != 'None' and reply != None:
                reply = reply.replace('[qq]', qq).replace('[sender]', name).replace('[intlove]', str(int_love)).replace(
                    '[love]', str_love).replace('[bot]', bot_name).replace('[vary]', str(love)).replace('\\n', '\n')
                reply = replace_alias(reply)
                reply, pic = pic_support(reply)
                if pic != None:
                    await bot.send(event, [reply, Image(path='.\data\pic\group\\'+groupid+'\\'+pic)])
                else:
                    await bot.send(event, reply)
                if love != 0 and love != None:
                    updata_love(qq, love)
                    logger.debug('已更新用户好感')
            mark_achieve()
            return None
        except:
            pass


@bot.on(GroupMessage, priority=1)
async def ffwsfcs(event: GroupMessage):
    if isAchieve == True:
        return None
    msg = str(event.message_chain)
    groupid = str(event.sender.group.id)
    qq = str(event.sender.id)
    a = check_admin(groupid, qq)

    def find_images(path, filename):
        image_formats = ['*.jpeg', '*.jpg', '*.png']
        for format_ in image_formats:
            files = glob.glob(os.path.join(path, filename + format_))
            if files:
                return os.path.basename(files[0])
        return None
    if msg == '/clear' and botreact == 'True':
        clear_memory(qq)
        await bot.send(event, '刚刚我们说什么了喵~')
        mark_achieve()
        logger.debug(f'{qq}记忆清除')
    if msg.startswith('/set senior '):
        if qq == master:
            msg = msg.replace('/set senior ', '')
            write_admin(groupid, 'high', msg)
            await bot.send(event, '成功设置高管喵~')
            logger.debug('设置'+msg+'为'+groupid+'高管')
            mark_achieve()
    elif msg.startswith('/set admin '):
        if qq == master or a == 'high':
            msg = msg.replace('/set admin ', '')
            write_admin(groupid, 'common', msg)
            await bot.send(event, '成功设置管理喵~')
            logger.debug('设置'+msg+'为'+groupid+'管理')
            mark_achieve()
    elif msg.startswith('/del admin '):
        if qq == master or a == 'high':
            msg = msg.replace('/del admin ', '')
            del_admin(groupid, msg)
            await bot.send(event, '成功取消管理喵~')
            logger.debug('取消'+msg+'为'+groupid+'管理')
            mark_achieve()
    elif msg.startswith('/del senior '):
        if qq == master:
            msg = msg.replace('/del senior ', '')
            del_admin_high(groupid, msg)
            await bot.send(event, '成功取消高管喵~')
            logger.debug('取消'+msg+'为'+groupid+'高管')
            mark_achieve()
    elif silence == True:
        return None
    elif msg.startswith('删除 '):
        if qq == master or a != False:
            question = msg.replace('删除 ', '')
            group_del(groupid, question)
            await bot.send(event, '成功删除回复喵~')
            mark_achieve()
    elif msg.startswith('精确问 '):
        if qq == master or a != False:
            msg = msg.replace('精确问 ', '')
            msg = msg.split(' ', 1)
            question = msg[0]
            answer = msg[1]
            if Image in event.message_chain:
                image = event.message_chain[Image][0]
                answer = answer.replace('[图片]', '')
                path = check_group_folder(groupid)
                filename = generate_random_string()
                await image.download(filename=f'{path}{filename}.jpeg')
                add = find_images(path, filename)
                answer = f'{answer}[pic={add}]'
            group_write(groupid, question, answer, '1')
            await bot.send(event, '成功设置回复喵~')
            logger.debug('写入新回复')
            mark_achieve()
    elif msg.startswith('模糊问 '):
        if qq == master or a != False:
            msg = msg.replace('模糊问 ', '')
            msg = msg.split(' ', 1)
            question = msg[0]
            answer = msg[1]
            if Image in event.message_chain:
                image = event.message_chain[Image][0]
                answer = answer.replace('[图片]', '')
                path = check_group_folder(groupid)
                filename = generate_random_string()
                await image.download(filename=f'{path}{filename}.jpeg')
                add = find_images(path, filename)
                answer = f'{answer}[pic={add}]'
            group_write(groupid, question, answer, '2')
            await bot.send(event, '成功设置回复喵~')
            logger.debug('写入新回复')
            mark_achieve()
    elif msg.startswith('查询 '):
        if qq == master or a != False:
            msg = msg.replace('查询 ', '')
            answers = find_row(groupid, msg)
            global reply_answer
            reply_answer = '查询到'+msg+'有以下回复喵:\n'
            for answer in answers:
                reply_answer = reply_answer+answer+'\n'
            await bot.send(event, reply_answer+'请使用/dr指令删除指定行喵~')
            del reply_answer
            mark_achieve()
    elif msg.startswith('/dr '):
        if qq == master or a != False:
            msg = msg.replace('/dr ', '')
            msg = msg.split(' ')
            try:
                msg = [int(s) for s in msg]
                success, fail = del_row(groupid, msg)
                if success == 0 and fail == 0:
                    raise Exception
                msg = '成功删除'+str(success)+'行，删除失败(由于锁定)'+str(fail)+'行喵~'
                await bot.send(event, msg)
            except:
                await bot.send(event, '删除指定行失败喵~')
            finally:
                mark_achieve()
    elif msg.startswith('/lock '):
        if qq == master or a == 'high':
            msg = msg.replace('/lock ', '')
            msg = msg.split(' ')
            try:
                lock_row(groupid, msg, 0)
                await bot.send(event, '锁定成功喵~')
            except:
                await bot.send(event, '输入不合法喵~行号可通过 查询 指令获取喵~')
            finally:
                mark_achieve()
    elif msg.startswith('/unlock '):
        if qq == master or a == 'high':
            msg = msg.replace('/unlock ', '')
            msg = msg.split(' ')
            try:
                lock_row(groupid, msg, 1)
                await bot.send(event, '解锁成功喵~')
            except:
                await bot.send(event, '输入不合法喵~行号可通过 查询 指令获取喵~')
            finally:
                mark_achieve()
    elif msg.startswith('/info '):
        if qq == master or a != False:
            msg = msg.replace('/info ', '')
            try:
                msg = int(msg)
                data = load_info(groupid, msg)
                if data == None:
                    raise Exception
                else:
                    reply = f"触发词: {data[0]}\n回复: {data[1]}\n好感增减范围: {data[2]}\n好感触发: {data[3]}\n类型: {data[4]}(1=精确,2=模糊)\n状态: {data[5]}"
                await bot.send(event, reply)
            except:
                await bot.send(event, '输入不合法喵~行号可通过 查询 指令获取喵~')
            finally:
                mark_achieve()


@bot.on(GroupMessage, priority=1)
async def sadxchjw(event: GroupMessage):
    if isAchieve == True:
        return None
    if str(event.message_chain) == '我的好感度' or str(event.message_chain) == '我的好感':
        qq = str(event.sender.id)
        int_love, str_love = get_both_love(qq)
        if str_love != '' or None:
            if lv_enable != 'True':
                await bot.send(event, '你的好感度是：\n'+str_love+'\n————————\n(ˉ▽￣～) 切~~')
                mark_achieve()
            elif lv_enable == "True":
                name = event.sender.get_name()
                name = str(name)
                lv = get_range(int_love)
                logger.debug('用户好感等级'+str(lv))
                if qq in pic_dict:
                    ico = event.sender.get_avatar_url()
                    path = choose_pic(qq)
                    pic = pic_reply(qq, name, path, ico)
                    await bot.send(event, Image(base64=pic), True)
                elif lv == 1:
                    lv1_need_reply = lv1_reply.replace('[qq]', qq).replace('[sender]', name).replace(
                        '[intlove]', str(int_love)).replace('[love]', str_love).replace('[bot]', bot_name)
                    lv1_need_reply = replace_alias(lv1_need_reply)
                    await bot.send(event, [At(int(qq)), '\n'+lv1_need_reply])
                elif lv == 2:
                    lv2_need_reply = lv2_reply.replace('[qq]', qq).replace('[sender]', name).replace(
                        '[intlove]', str(int_love)).replace('[love]', str_love).replace('[bot]', bot_name)
                    lv2_need_reply = replace_alias(lv2_need_reply)
                    await bot.send(event, [At(int(qq)), '\n'+lv2_need_reply])
                elif lv == 3:
                    lv3_need_reply = lv3_reply.replace('[qq]', qq).replace('[sender]', name).replace(
                        '[intlove]', str(int_love)).replace('[love]', str_love).replace('[bot]', bot_name)
                    lv3_need_reply = replace_alias(lv3_need_reply)
                    await bot.send(event, [At(int(qq)), '\n'+lv3_need_reply])
                elif lv == 4:
                    lv4_need_reply = lv4_reply.replace('[qq]', qq).replace('[sender]', name).replace(
                        '[intlove]', str(int_love)).replace('[love]', str_love).replace('[bot]', bot_name)
                    lv4_need_reply = replace_alias(lv4_need_reply)
                    await bot.send(event, [At(int(qq)), '\n'+lv4_need_reply])

                elif lv == 5:
                    lv5_need_reply = lv5_reply.replace('[qq]', qq).replace('[sender]', name).replace(
                        '[intlove]', str(int_love)).replace('[love]', str_love).replace('[bot]', bot_name)
                    lv5_need_reply = replace_alias(lv5_need_reply)
                    await bot.send(event, [At(int(qq)), '\n'+lv5_need_reply])
                else:
                    logger.warning('好感等级未能覆盖所有用户')
                    if int_love <= La:
                        await bot.send(event, bot_name+'不想理你\n'+str_love)
                    else:
                        await bot.send(event, bot_name+'很中意你\n'+str_love)
                mark_achieve()
    elif str(event.message_chain) == '我的排名':
        qq = str(event.sender.id)
        name = event.sender.get_name()
        rank, total = get_loverank(qq)
        await bot.send(event, [At(int(qq)), f'\n{name}的好感排名为[{rank}/{total}]'])
        logger.debug('完成个人排名')
        mark_achieve()


@bot.on(GroupMessage, priority=1)
async def gegvsgverg(event: GroupMessage):
    if isAchieve == True:
        return None
    msg = str(event.message_chain)
    if msg.startswith('查询好感'):
        msg = msg.replace('查询好感', '')
        try:
            msg = int(msg)
            qq = str(msg)
        except:
            msg = event.message_chain.as_mirai_code()
            msg = msg.replace('查询好感', '')
            qq = msg.replace('[mirai:at:', '').replace(']', '')
        int_love, str_love = get_both_love_obly(qq)
        if str_love != None:
            global search_love_reply
            reply = search_love_reply
            name = await bot.get_group_member(event.group.id, int(qq))
            try:
                name = name.member_name
            except:
                name = ''
            if name == None:
                name = ''
            qq = replace_alias(qq)
            reply = reply.replace('[qq]', qq).replace('[sender]', name).replace('[intlove]', str(
                int_love)).replace('[love]', str_love).replace('[bot]', bot_name).replace('\\n', '\n')
            await bot.send(event, reply)
        else:
            await bot.send(event, '查无此人喵~')
        mark_achieve()


@bot.on(GroupMessage, priority=1)
async def jjjjjj(event: GroupMessage):
    if bot_name in str(event.message_chain):
        a = random.random()
        if rate >= a:
            logger.debug('发送概率判断成功')
            qq = str(event.sender.id)
            int_love, _ = get_both_love(qq)
            if int_love >= baseline:
                logger.debug('baseline判断成功')
                # 获取当前时间戳
                current_ts = current_timestamp()
                # 读取用户最后判断时间戳
                last_ts = get_user_timestamp(qq)
                # 如果时间戳不存在或超过当前日期（即今天上午9点之前）
                if last_ts is None or last_ts < (current_ts - (current_ts % (24 * 60 * 60)) + 9 * 60 * 60):
                    # 更新时间戳为今天的时间（上午9点）
                    update_user_timestamp(
                        qq, current_ts - (current_ts % (24 * 60 * 60)) + 9 * 60 * 60)
                    logger.debug('时间戳判断成功')
                    # 获取文件夹中所有图片文件（.jpg或.png）
                    images = [f for f in os.listdir(image_folder) if f.endswith(
                        '.jpg') or f.endswith('.png')]
                    # 如果文件夹中有图片，随机选择一张
                    if images:
                        path2 = os.path.join(
                            image_folder, random.choice(images))
                        logger.debug(path2)
                        await bot.send(event, Image(path=path2), True)
                        logger.debug('CG发送成功')


@bot.on(GroupMessage, priority=1)
async def fascfvnewjk(event: GroupMessage):
    if isAchieve == True or tank_enable != 'True':
        return None
    msg = str(event.message_chain)
    if msg == '/gtank':
        mark_achieve()
        await bot.send(event, '请在120s内中发送表图喵~')

        @GroupMessageFilter(group_member=event.sender)
        def T114514(event_new: GroupMessage):
            if Image in event_new.message_chain:
                out_image = event_new.message_chain[Image][0]
                return out_image
        out_image = await inc.wait(T114514, timeout=120)
        out_image = out_image.url
        await bot.send(event, '请在120s内发送里图喵~')

        @GroupMessageFilter(group_member=event.sender)
        def T114514_2(event_new: GroupMessage):
            if Image in event_new.message_chain:
                hidden_image = event_new.message_chain[Image][0]
                return hidden_image
        hidden_image = await inc.wait(T114514_2, timeout=120)
        hidden_image = hidden_image.url
        tank = hidden_pic(out_image, hidden_image, 0)
        logger.debug('合成幻影坦克')
        await bot.send(event, Image(base64=tank), True)


@bot.on(FriendMessage, priority=1)
async def hhhhhh(event: FriendMessage):
    qq = str(event.sender.id)
    msg = str(event.message_chain)
    if qq == master and msg.startswith('/encode alias '):
        msg = msg.replace('/encode alias ', '')
        b = int(0)
        await bot.send(event, '确认无误请回复"确认"')
        logger.debug('alias_code生成中')

        @FriendMessageFilter(friend=event.sender)
        def T9(event_new: FriendMessage):
            msg2 = str(event_new.message_chain)
            if msg2 == '确认':
                return True
            else:
                return False
        c = await inc.wait(T9, timeout=120)
        if c == True:
            try:
                msg = int(msg)
                generate_codes(msg, b)
                await bot.send(event, '生成完毕')
                logger.debug('alias_code生成完毕')
            except:
                await bot.send(event, '数值不合法')
                logger.debug('alias_code生成失败')
        elif c == False:
            await bot.send(event, '已取消code生成')
            logger.debug('alias_code取消生成')
    elif qq == master and msg.startswith('/encode love '):
        msg = msg.replace('/encode love ', '')
        b = int(1)
        await bot.send(event, '确认无误请回复"确认"')
        logger.debug('love_code生成中')

        @FriendMessageFilter(friend=event.sender)
        def T8(event_new: FriendMessage):
            msg2 = str(event_new.message_chain)
            if msg2 == '确认':
                return True
            else:
                return False
        c = await inc.wait(T8, timeout=120)
        if c == True:
            try:
                msg = int(msg)
                generate_codes(msg, b)
                await bot.send(event, '生成完毕')
                logger.debug('love_code生成完毕')
            except:
                await bot.send(event, '数值不合法')
                logger.debug('love_code生成失败')
        elif c == False:
            await bot.send(event, '已取消code生成')
            logger.debug('love_code取消生成')
    elif qq == master and msg.startswith('/encode pic '):
        msg = msg.replace('/encode pic ', '')
        b = int(2)
        await bot.send(event, '确认无误请回复"确认"')
        logger.debug('pic_code生成中')

        @FriendMessageFilter(friend=event.sender)
        def T7(event_new: FriendMessage):
            msg2 = str(event_new.message_chain)
            if msg2 == '确认':
                return True
            else:
                return False
        c = await inc.wait(T7, timeout=120)
        if c == True:
            try:
                msg = int(msg)
                generate_codes(msg, b)
                await bot.send(event, '生成完毕')
                logger.debug('pic_code生成完毕')
            except:
                await bot.send(event, '数值不合法')
                logger.debug('pic_code生成失败')
        elif c == False:
            await bot.send(event, '已取消code生成')
            logger.debug('pic_code取消生成')


@bot.on(GroupMessage, priority=1)
async def dewcfvew(event: GroupMessage):
    global reply_b
    qq_list = None
    reply_b = str('好♡感♡排♡行\n')
    if str(event.message_chain) == '好感排行':
        qq_list = GlobalCompare()
        mark_achieve()
    elif str(event.message_chain) == '好人榜':
        qq_list = get_low_ten_qqs()
        mark_achieve()
    if qq_list != None:
        for i in qq_list:
            a = str(i)
            _, love = get_both_love(i)
            reply_b = reply_b+a+' : '+love+'\n'
        reply_b = replace_alias(reply_b)
        await bot.send(event, reply_b + '--------\n喵呜~~~')
    del reply_b


@bot.on(GroupMessage, priority=1)
async def dewcfvew(event: GroupMessage):
    if isAchieve == True:
        return None
    global reply_a
    reply_a = str('本群 好♡感♡排♡行\n')
    if str(event.message_chain) == '本群好感排行':
        list = await bot.member_list(event.sender.group.id)
        ids = [member.id for member in list]
        results = [(str(id), *get_both_love(str(id)))
                   for id in ids]  # 使用解包获取int_value和str_value
        sorted_results = sorted(
            results, key=lambda x: x[1], reverse=True)  # 按int_value降序排序
        top_10_results = sorted_results[:10]
        formatted_top_10 = [f"{id} : {str_value}" for id,
                            _, str_value in top_10_results]
        for item in formatted_top_10:
            a = str(item)
            reply_a = reply_a+a+'\n'
        reply_a = replace_alias(reply_a)
        await bot.send(event, reply_a + '--------\n喵呜~~~')
        del reply_a
        mark_achieve()


@bot.on(GroupMessage, priority=1)
async def alias(event: GroupMessage):
    if isAchieve == True:
        return None
    message = str(event.message_chain)
    if message.startswith('/code alias '):
        mark_achieve()
        message = message.replace('/code alias ', '')
        b = check_alias_code(message)
        if b == True:
            logger.debug('code正确')
            qq = str(event.sender.id)
            code_record(qq+'使用'+message+'作为QQ别名')
            await bot.send(event, '请在120s内发送您要设置的QQ别名喵~')

            @GroupMessageFilter(group_member=event.sender)
            def T10(event_new: GroupMessage):
                msg = str(event_new.message_chain)
                return msg
            msg = await inc.wait(T10, timeout=120)
            update_alias(qq, msg)
            await bot.send(event, '您的QQ别名已设置为:'+msg+' 喵~')


@bot.on(GroupMessage, priority=1)
async def strqq(event: GroupMessage):
    message = str(event.message_chain)
    if message.startswith('/code love '):
        mark_achieve()
        message = message.replace('/code love ', '')
        b = check_love_code(message)
        if b == True:
            logger.debug('code正确')
            qq = str(event.sender.id)
            code_record(qq+'使用'+message+'作为文本好感')
            await bot.send(event, '请在120s内发送您要设置的文本好感喵~')

            @GroupMessageFilter(group_member=event.sender)
            def T11(event_new: GroupMessage):
                msg = str(event_new.message_chain)
                return msg
            msg = await inc.wait(T11, timeout=120)
            write_str_love(qq, ' '+msg)
            read_qq_txt_to_dict()
            await bot.send(event, '您的文本好感已设置为:'+msg+' 喵~')


@bot.on(GroupMessage, priority=1)
async def picqq(event: GroupMessage):
    message = str(event.message_chain)
    if message.startswith('/code pic '):
        mark_achieve()
        message = message.replace('/code pic ', '')
        b = check_pic_code(message)
        if b == True:
            logger.debug('code正确')
            qq = str(event.sender.id)
            code_record(qq+'使用'+message+'作为pic')
            await bot.send(event, '请在120s内发送您要设置的图片喵~')

            @GroupMessageFilter(group_member=event.sender)
            def T12(event_new: GroupMessage):
                if Image in event_new.message_chain:
                    image = event_new.message_chain[Image][0]
                    return image
            image = await inc.wait(T12, timeout=120)
            await image.download(filename='./data/images/'+qq+'.jpeg')
            write_pic(qq, '1')
            read_pic_to_dict()
            await bot.send(event, '您的pic已设置喵~', True)


@bot.on(GroupMessage, priority=1)
async def fegsg(event: GroupMessage):
    if isAchieve == True:
        return None

    def del_face(text: str) -> str:
        result = re.sub(face_del, '', text)
        return result
    message = event.message_chain.as_mirai_code()
    message = re.sub(r'\[mirai:.*?\]', '', message)
    # message = message.replace('[图片]', '').replace(bot_name, '菲菲')
    if message == '':
        return None
    # s = snownlp.SnowNLP(message)
    # sentiment_score = float(s.sentiments)
    reply = None
    isSend = False
    name = str(event.sender.get_name())
    qq = str(event.sender.id)
    if memory != False:
        intlove = read_love(qq)
    else:
        intlove = 0
    if bot_name in message or At(bot.qq) in event.message_chain:
        isSend = True
        if At(bot.qq) in event.message_chain and botreact == 'True':
            s = snownlp.SnowNLP(message)
            sentiment_score = float(s.sentiments)
            a = new_msg_judge(message)
            # if a == True:
            if sentiment_score <= 0.1 or model == 'qingyunke':
                message = message.replace(bot_name, '菲菲')
                reply = await qingyunke(message)
            else:
                reply = await baidu_ai(message, qq, intlove, name)
            message = message.replace('菲菲', '')
            love = love_score(message)
            logger.debug('情感运算')
            if love != 0 and a == True:
                updata_love(qq, love)
                logger.debug(qq+'情感运算'+str(love))
            elif a == False:
                updata_love(qq, -3)
                logger.debug('重复消息')
            if reply != None:
                reply = str(reply)
                reply = reply.replace('菲菲', bot_name)
                reply = del_face(reply)
                await bot.send(event, reply, True)
            # else:
            #    logger.debug('重复消息')
            mark_achieve()
    m = random.random()
    if m <= 0.004 and botreact == 'True' and isSend == False:
        s = snownlp.SnowNLP(message)
        sentiment_score = float(s.sentiments)
        if sentiment_score <= 0.1 or model == 'qingyunke':
            message = message.replace(bot_name, '菲菲')
            reply = await qingyunke(message)
        else:
            reply = await baidu_ai(message, qq, intlove, name)
        s2 = SnowNLP(message)
        key = s2.keywords(1)
        message = message.replace('菲菲', '')
        love = love_score(message)
        if love >= 5:
            extra = '\n'+bot_name+'其实不讨厌“'+key[0]+'"这个词喵~'
        elif love <= -5:
            extra = '\n'+bot_name+'讨厌“'+key[0]+'"这个词喵~'
        else:
            extra = ''
        reply = reply+extra
        logger.debug('情感运算')
        if love != 0:
            updata_love(qq, love)
            logger.debug(qq+'情感运算'+str(love))
        if reply != None:
            reply = str(reply)
            reply = reply.replace('菲菲', bot_name)
            reply = del_face(reply)
            await bot.send(event, [At(int(qq)), ' '+reply])
        mark_achieve()


# 函数注册表
function_registry = {
    "get_love": ws_load_love,  # 需要qq
    "change_love": ws_change_love,  # 需要qq和love
    "get_lv": ws_get_range,  # 需要qq
    'get_rank': ws_get_rank,
    "isAdmin": check_admin,
    "silence": isSilence,
    'love_score': love_score
}

# 辅助函数，用于检查参数并调用函数


def call_function(func, data):
    sig = inspect.signature(func)
    bound_args = sig.bind(**data)
    bound_args.apply_defaults()
    try:
        return func(*bound_args.args, **bound_args.kwargs)
    except TypeError as e:
        logger.warning(f"Invalid parameters for function {func.__name__}: {e}")
        return "error: invalid parameters"


async def websocket_handler(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
            function_type = data.get("type")

            if function_type in function_registry:
                func = function_registry[function_type]
                result = call_function(
                    func, {k: v for k, v in data.items() if k != "type"})
                await websocket.send(result)
            else:
                await websocket.send("Unknown function type")

        except json.JSONDecodeError:
            await websocket.send("Invalid JSON")

    # 启动WebSocket服务器


async def start_server():
    global stop_future
    stop_future = asyncio.get_event_loop().create_future()
    while True:
        async with websockets.serve(websocket_handler, "localhost", ws_port) as server:
            logger.info('ws运行在'+str(ws_port))
            await server.wait_closed()


def real_start_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())
    loop.close()


ws_thread = threading.Thread(target=real_start_server)
if ws == "True":
    ws_thread.start()
else:
    logger.info('ws服务被禁用')
del ws, ws_thread
retry = False
try:
    logger.info('Ciallo～(∠・ω< )⌒★')
    bot.run()
except Exception:
    logger.warning('无法连接到mirai,当前仅启用ws。15s后尝试重连。')
    retry = True
    time.sleep(15)
try:
    while retry == True:
        try:
            logger.info('Ciallo～(∠・ω< )⌒★')
            bot.run()
        except Exception:
            logger.warning('无法连接到mirai。30s后尝试重连。')
            time.sleep(30)
except KeyboardInterrupt:
    logger.info('取消重连尝试,现仅启用ws/空载运行')
