from mirai import Mirai, WebSocketAdapter, GroupMessage,Image,FriendMessage,At
from mirai_extensions.trigger.message import GroupMessageFilter
from mirai_extensions.trigger.trigger import *
from mirai_extensions.trigger import InterruptControl
import pandas as pd      
import random
import os  
import re  
import shutil  
import tempfile     
import os  
import re  
import shutil  
import tempfile 
import logging 
import colorlog
import time
import sys
import configparser
import requests
py_version='v1.21.3-beta1'

csv_path = './data/reply.csv'  # 替换为你的CSV文件路径
config = configparser.ConfigParser() 
image_folder = '.\data\CG'
#只是log
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
   df = pd.read_csv(csv_path, header=None)  # 假设没有列名，使用header=None
   logger.info('reply.csv已成功加载')
except:
   logger.error('未能成功读取reply.csv,请确认文件是否存在')
   logger.error('程序将在5秒后退出')
   time.sleep(5)
   sys.exit()


def loadconfig():
   # 读取配置文件
   fp_dir = os.getcwd() #取得的是exe文件路径
   path = os.path.join(fp_dir, "config.ini") #拼接上配置文件名称目录  
   try:
      config.read(path,encoding='utf-8')
      logger.info('正在加载config.ini') 
   except :
      logger.error('无法加载config.ini,请检查文件是否存在或填写格式是否正确')
      logger.error('程序将在5秒后退出')
      time.sleep(5)
      sys.exit

   # 获取配置项的值  
   bot_qq = config.get('bot', 'bot_qq')  
   verify_key = config.get('bot', 'verify_key')  
   host = config.get('bot', 'host')  
   port = config.get('bot', 'port')
   bot_name=config.get('others','bot_name')
   baseline=config.getint('random_CG','baseline')
   rate=config.getfloat('random_CG','rate')
   master=config.get('others','master')
   lv_enable=config.get('lv','enable')
   logger.info('config.ini第一部分已成功加载')
   return  bot_qq,verify_key,host,port,bot_name,baseline,rate,master,lv_enable

bot_qq,verify_key,host,port,bot_name,baseline,rate,master,lv_enable=loadconfig()

  
def get_range(value):  
    if La <= value < Lb: 
        logger.debug('获得lv1') 
        return  1 
    elif Lc <= value < Ld:  
        logger.debug('获得lv2')
        return  2
    elif Le <= value < Lf:
        logger.debug('获得lv3')  
        return  3
    elif Lg <= value < Lh:
        logger.debug('获得lv4')  
        return  4
    elif Li <= value < Lj:
        logger.debug('获得lv5')  
        return  5
    else:
        logger.debug('未获得lv')  
        return None  # 返回None表示不属于任何已知范围
      

def loadconfig_part2():
   # 读取配置文件
   fp_dir = os.getcwd() #取得的是exe文件路径
   path = os.path.join(fp_dir, "config.ini") #拼接上配置文件名称目录  
   try:
      config.read(path,encoding='utf-8')
      logger.info('正在加载第二部分config.ini')
      lv1= config.get('lv','lv1')
      a, b = (value.strip() for value in lv1.split(','))
      lv2= config.get('lv','lv2')
      c, d = (value.strip() for value in lv2.split(','))
      lv3= config.get('lv','lv3')
      e, f = (value.strip() for value in lv3.split(','))
      lv4= config.get('lv','lv4')
      g, h = (value.strip() for value in lv4.split(','))
      lv5= config.get('lv','lv5')
      i, j = (value.strip() for value in lv5.split(','))
      lv1_reply=config.get('lv','lv1_reply')
      lv1_reply=lv1_reply.replace('\\n','\n')
      lv2_reply=config.get('lv','lv2_reply')
      lv2_reply=lv2_reply.replace('\\n','\n')
      lv3_reply=config.get('lv','lv3_reply')
      lv3_reply=lv3_reply.replace('\\n','\n')
      lv4_reply=config.get('lv','lv4_reply')
      lv4_reply=lv3_reply.replace('\\n','\n')
      lv5_reply=config.get('lv','lv5_reply')
      lv5_reply=lv3_reply.replace('\\n','\n')
      logger.info('config.ini第二部分已成功加载')
      return a,b,c,d,e,f,g,h,i,j,lv1_reply,lv2_reply,lv3_reply,lv4_reply,lv5_reply
   except:
      logger.error('无法加载config.ini,请检查文件是否存在或填写格式是否正确')
      logger.error('程序将在5秒后退出')
      time.sleep(5)
      sys.exit       

if lv_enable=='True':
   logger.info('初始化好感等级...')
   La,Lb,Lc,Ld,Le,Lf,Lg,Lh,Li,Lj,lv1_reply,lv2_reply,lv3_reply,lv4_reply,lv5_reply=loadconfig_part2()
   try:
       La=int(La)
       Lb=int(Lb)
       Lc=int(Lc)
       Ld=int(Ld)
       Le=int(Le)
       Lf=int(Lf)
       Lg=int(Lg)
       Lh=int(Lh)
       Li=int(Li)
       Lj=int(Lj)
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
    response = requests.get("https://api.github.com/repos/hlfzsi/yirimirai_LoveYou/releases/latest")
    py_update=(response.json()["tag_name"])
    if py_version!=py_update:
        logger.warning('本项目有更新,请前往https://github.com/hlfzsi/yirimirai_LoveYou/releases\n'+'当前版本:'+py_version)
    else:
        logger.info('当前已为最新版本'+py_version) 
except:
    logger.warning('未连接到网络,无法检查更新')
time.sleep(3)

def pic_support(text):  
    # 正则表达式匹配 [pic=任意图片名.(png|jpg)]  
    pattern = r'\[pic=(.*?\.(png|jpg))\]'  
      
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

def update_alias(qq, str_value,alias_file='./data/alias.txt'):  
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
        alias_dict=read_alias()  
  
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
alias_dict=read_alias()

def current_timestamp():  
    return int(time.time())

# 写入或更新用户的最后判断时间戳  
def update_user_timestamp(user_id, timestamp):  
    with open('./data/recoder.txt', 'a+') as f:  
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
        with open('./data/recoder.txt', 'r') as f:  
            for line in f:  
                if line.startswith(str(user_id) + '='):  
                    return int(line.split('=')[1].strip())
                logger.debug('时间戳读取完成')  
        return None  
    except FileNotFoundError:  
        logger.warning('./data/recoder.txt丢失')
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

def update_txt(qq, hgbh, txt_filename='./data/qq.txt'):    
  
    # 读取文件的所有行到列表中  
    with open(txt_filename, 'r', encoding='utf-8') as file:  
        lines = file.readlines()  
  
    # 使用临时文件来避免直接覆盖原文件  
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as temp_file:  
        updated = False  
        for line in lines:  
            if line.strip().startswith(f'{qq}='):  
                match = re.search(r'{qq}=(\d+)(.*)$'.format(qq=qq), line)  
                if match:  
                    number = int(match.group(1)) + hgbh  
                    new_line = f'\n{qq}={number}{match.group(2)}'  
                    temp_file.write(new_line)  
                    updated = True  
                else:  
                    temp_file.write(line)  
            else:  
                temp_file.write(line)  
  
        # 如果未更新，则添加新行  
        if not updated:  
            temp_file.write(f'\n{qq}={hgbh}') 
            logger.debug('新行已添加') 
  
    # 使用shutil来替换原文件，确保原子操作  
    shutil.move(temp_file.name, txt_filename)  
  
    # 清理临时文件（如果函数成功执行）  
    try:  
        os.remove(temp_file.name)
        logger.debug('清理临时文件')  
    except OSError as e:  
        logger.debug(f"Error: {e.strerror} : {temp_file.name}")
        logger.debug('已清理')
  
def change_txt(search_term, m):  
    
    # 筛选匹配第一列的行      
    matches = df[df.iloc[:, 0] == search_term]      
  
    # 过滤掉第四列(c, d)范围不包含m的行，并处理空值    
    def is_m_in_range(row):    
        cd_str = str(row.iloc[3])    
        if cd_str.strip() == "nan":  # 如果为空值或空字符串，则认为m符合范围    
            return True    
        try:    
            c, d = map(int, cd_str.strip('()').split(','))    
            return c <= m <= d  # 检查 m 是否在 (c, d) 范围内    
        except ValueError:  # 如果无法转换为整数    
            return False    
  
    # 假设 matches 是一个pandas DataFrame，且第四列是字符串形式的范围，如"(1, 5)"    
    # 或者第四列可能包含空值或无法转换为整数的字符串    
    valid_matches = matches.apply(is_m_in_range, axis=1)  
    valid_matches = matches[valid_matches]  
  
    # 如果没有找到匹配的行，返回None      
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
    logger.debug('完成回复配对')
    return reply, love      

def extract_numbers_from_string_iterative(input_string):  
    # 初始化一个空字符串来保存数字  
    numbers = ''  
    # 遍历输入字符串的每个字符  
    for char in input_string:  
        # 如果字符是数字，则添加到结果字符串中  
        if char.isdigit():  
            numbers += char  
    # 返回结果字符串  
    return numbers  
  
def read_txt(qq, filename='./data/qq.txt'):
    int_love = None
    str_love = None

    # 尝试读取和修改文件
    with open(filename, 'r+', encoding='utf-8') as file:
        # 读取文件内容
        content = file.readlines()
        
        # 检查是否有匹配的qq
        for line in content:
            if line.startswith(qq + '='):
                # 提取等号之后的内容
                value = line.split('=')[1].strip()
                # 尝试将内容转换为整数
                try:
                    int_love = int(extract_numbers_from_string_iterative(value))
                except ValueError:
                    # 如果不能转换为整数，则只将文本赋值给str_love
                    str_love = value
                    int_love = 0
                else:
                    # 如果能转换为整数，同时赋值给str_love
                    str_love = value
                break  # 找到匹配项后退出循环

        # 如果没有找到匹配的qq，在文件末尾添加新条目
        if str_love is None:
            new_line = f'\n{qq}=0'
            file.write(new_line)  # 由于已经处于文件末尾，可以直接写入
            str_love = '0'  # 设置str_love为新添加的数值
            int_love= 0
            logger.debug('已新增行')
    logger.debug('读取好感度完成')
    return int_love, str_love       

def GlobalCompare(filename='./data/qq.txt'):  
    # 创建一个字典来存储b值和a函数的第二个返回值  
    b_values = {}  
      
    # 读取文件  
    with open(filename, 'r', encoding='utf-8') as file:  
        lines = file.readlines()  
      
    # 处理每一行  
    for line in lines:  
        if '=' in line:  
            key, value = line.strip().split('=', 1)  
            try:  
                b_value = key
                # 调用a函数并获取返回值  
                first_result, second_result = read_txt(b_value)  
                # 将b值和a函数的第二个返回值存储在字典中
                b_values[b_value] = second_result  
            except ValueError:  
                # 如果键不是整数，则忽略这一行  
                continue  
      
    # 根据a函数的第一个返回值对b值进行排序（降序）  
    sorted_b_values = sorted(b_values.items(), key=lambda x: read_txt(x[0])[0], reverse=True)  
      
    # 提取前十个最大的b值及其对应的a函数的第二个返回值  
    top_ten_b_values = [f'{b}'+' : '+ second_result for b, second_result in sorted_b_values[:10]]  
      
    return top_ten_b_values

if __name__ == '__main__':
    bot = Mirai(
        qq=bot_qq, # 改成你的机器人的 QQ 号
        adapter=WebSocketAdapter(
            verify_key=verify_key, host=host, port=port
        )
    )
inc = InterruptControl(bot)

@bot.on(GroupMessage)
async def bhrkhrt(event: GroupMessage):
    message =str(event.message_chain) 
    qq=str(event.sender.id)
    int_love,str_love=read_txt(qq)
    name=event.sender.get_name()
    message=message.replace(qq,'[qq]').replace(name,'[sender]').replace(str(int_love),'[intlove]').replace(str_love,'[love]').replace(bot_name,'[bot]').replace('\n','\\n')
    reply,love=change_txt(message,int_love)
    try:
        love = int(love)
    except:
        love = int(0)
    if reply != None:
        reply=reply.replace('[qq]',qq).replace('[sender]',name).replace('[intlove]',str(int_love)).replace('[love]',str_love).replace('[bot]',bot_name).replace('[vary]',str(love)).replace('\\n','\n')
        reply=replace_alias(reply)
        reply,pic=pic_support(reply)
        if pic != None:
           await bot.send(event,[reply,Image(path='.\data\pic\\'+pic)])
        else:
           await bot.send(event,reply)
    if love != 0:
        update_txt(qq,love)
        logger.debug('已更新用户好感')

@bot.on(GroupMessage)
async def sadxchjw(event: GroupMessage):
    if str(event.message_chain) == '我的好感度' or str(event.message_chain) == '我的好感':
        qq=str(event.sender.id)
        int_love,str_love=read_txt(qq)
        if str_love != ''or None:
           if lv_enable =='False':
               await bot.send(event,'你的好感度是：\n'+str_love+'\n————————\n(ˉ▽￣～) 切~~')
           elif lv_enable == "True":
               name=event.sender.get_name()
               name=str(name)
               lv=get_range(int_love)
               logger.debug('用户好感等级'+str(lv))
               if lv==1:
                   lv1_need_reply=lv1_reply.replace('[qq]',qq).replace('[sender]',name).replace('[intlove]',str(int_love)).replace('[love]',str_love).replace('[bot]',bot_name)
                   lv1_need_reply=replace_alias(lv1_need_reply)
                   await bot.send(event,[At(int(qq)),'\n'+lv1_need_reply])
               elif lv==2:
                   lv2_need_reply=lv2_reply.replace('[qq]',qq).replace('[sender]',name).replace('[intlove]',str(int_love)).replace('[love]',str_love).replace('[bot]',bot_name)
                   await bot.send(event,[At(int(qq)),'\n'+lv2_need_reply])
                   lv2_need_reply=replace_alias(lv2_need_reply)
               elif lv==3:
                   lv3_need_reply=lv3_reply.replace('[qq]',qq).replace('[sender]',name).replace('[intlove]',str(int_love)).replace('[love]',str_love).replace('[bot]',bot_name)
                   await bot.send(event,[At(int(qq)),'\n'+lv3_need_reply])
                   lv3_need_reply=replace_alias(lv3_need_reply)
               elif lv==4:
                   lv4_need_reply=lv4_reply.replace('[qq]',qq).replace('[sender]',name).replace('[intlove]',str(int_love)).replace('[love]',str_love).replace('[bot]',bot_name)
                   await bot.send(event,[At(int(qq)),'\n'+lv4_need_reply])
                   lv4_need_reply=replace_alias(lv4_need_reply)
               elif lv==5:
                   lv5_need_reply=lv5_reply.replace('[qq]',qq).replace('[sender]',name).replace('[intlove]',str(int_love)).replace('[love]',str_love).replace('[bot]',bot_name)
                   await bot.send(event,[At(int(qq)),'\n'+lv5_need_reply])
                   lv5_need_reply=replace_alias(lv5_need_reply)
               else:
                   logger.warning('好感等级未能覆盖所有用户')
                   if int_love <= 0:
                       await bot.send(event,bot_name+'不想理你\n'+str_love)
                   else:
                       await bot.send(event,bot_name+'很中意你\n'+str_love)
           else:
               logger.error('enable参数填写错误,应为True或False')
               logger.error('程序将在5秒后退出')
               time.sleep(5)
               sys.exit

               


@bot.on(GroupMessage)
async def jjjjjj(event:GroupMessage):
    if bot_name in str(event.message_chain):
        a=random.random()
        if rate >= a:
            logger.debug('发送概率判断成功')
            qq=str(event.sender.id)
            int_love,str_love=read_txt(qq)
            if int_love >= baseline:
              logger.debug('baseline判断成功')
              # 获取当前时间戳  
              current_ts = current_timestamp()  
              # 读取用户最后判断时间戳  
              last_ts = get_user_timestamp(qq)  
              # 如果时间戳不存在或超过当前日期（即今天上午9点之前）  
              if last_ts is None or last_ts < (current_ts - (current_ts % (24 * 60 * 60)) + 9 * 60 * 60):  
                  # 更新时间戳为今天的时间（上午9点）  
                  update_user_timestamp(qq, current_ts - (current_ts % (24 * 60 * 60)) + 9 * 60 * 60)
                  logger.debug('时间戳判断成功')
                  # 获取文件夹中所有图片文件（.jpg或.png）  
                  images = [f for f in os.listdir(image_folder) if f.endswith('.jpg') or f.endswith('.png')]  
                  # 如果文件夹中有图片，随机选择一张  
                  if images:  
                      path2 = os.path.join(image_folder, random.choice(images))
                      logger.debug(path2)
                      await bot.send(event,Image(path=path2),True)
                      logger.debug('CG发送成功') 

'''写一半不想写了
@bot.on(FriendMessage)
async def hhhhhh(event: FriendMessage):
    qq=str(event.sender)
    if qq == master and str(event.message_chain)=='/help LoveYou':
        await bot.send(event,'')
'''


@bot.on(GroupMessage)
async def dewcfvew(event: GroupMessage):
    global reply_b
    reply_b=str('好♡感♡排♡行\n')
    if str(event.message_chain) =='好感排行':
        qq_list=GlobalCompare  
        for item in qq_list():
            a=str(item)   
            reply_b=reply_b+a+'\n'
        reply_b=replace_alias(reply_b)
        await bot.send(event,reply_b + '--------\n喵呜~~~')


@bot.on(GroupMessage)
async def dewcfvew(event: GroupMessage):
    global reply_a
    reply_a=str('本群 好♡感♡排♡行\n')
    if str(event.message_chain) =='本群好感排行':
        list=await bot.member_list(event.sender.group.id)
        ids = [member.id for member in list]
        results = [(str(id), *read_txt(str(id))) for id in ids]  # 使用解包获取int_value和str_value  
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)  # 按int_value降序排序
        top_10_results = sorted_results[:10]
        formatted_top_10 = [f"{id} : {str_value}" for id, int_value, str_value in top_10_results]
        for item in formatted_top_10:
            a=str(item)   
            reply_a=reply_a+a+'\n'
        reply_a=replace_alias(reply_a)
        await bot.send(event,reply_a + '--------\n喵呜~~~')


@bot.on(GroupMessage)
async def alias(event: GroupMessage):
    message=str(event.message_chain)
    if message.startswith('/code alias '):
        message=message.replace('/code alias ','')
        b=check_alias_code(message)
        if b==True:
          logger.debug('code正确')
          qq=str(event.sender.id)
          await bot.send(event,'请在120s内发送您要设置的QQ别名喵~')
          @GroupMessageFilter(group_member=event.sender)
          def T10(event_new: GroupMessage):
                  msg = str(event_new.message_chain)
                  return msg
          msg=await inc.wait(T10,timeout=120)
          update_alias(qq,msg)
          await bot.send(event,'您的QQ别名已设置为:'+msg+' 喵~')








          '''
          await bot.send(event,'请在120s内发送您要设置的QQ别名喵~\n不可以有数字喵~')
          @GroupMessageFilter(group_member=event.sender)
          def T11(event_new: GroupMessage):
                  msg = str(event_new.message_chain)
                  return msg
          a=False
          msg=await inc.wait(T11,timeout=120)
          while a==False:
            if extract_numbers_from_string_iterative(msg)=='':
                update_alias(qq,msg)
                await bot.send(event,'您的QQ别名已设置为:'+msg+' 喵~')
                a=True
            else:
                await bot.send(event,'请不要包含数字喵~')
                Trigger.reset(T11)
        else:
            await bot.send(event,'不存在该code喵~')
            '''
try:
       bot.run()
except Exception:
        logger.error(Exception)
        input("按任意键退出")
