from mirai import Mirai, WebSocketAdapter, GroupMessage
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
csv_path = 'reply.csv'  # 替换为你的CSV文件路径
config = configparser.ConfigParser()
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


def loadbot():
   # 读取配置文件  
   try:
      config.read('config.ini')
      logger.info('正在加载config.ini') 
   except :
      logger.error('无法加载config.ini,请确认文件是否存在或填写格式是否正确')
      logger.error('程序将在5秒后退出')
      time.sleep(5)
      sys.exit

   # 获取配置项的值  
   bot_qq = config.get('bot', 'bot_qq')  
   verify_key = config.get('bot', 'verify_key')  
   host = config.get('bot', 'host')  
   port = config.get('bot', 'port')
   logger.info('config.ini已成功加载')
   time.sleep(3) 
   return  bot_qq,verify_key,host,port

bot_qq,verify_key,host,port=loadbot()

def update_txt(qq, hgbh, txt_filename='qq.txt'):  
    #qq = str(qq)  
    #hgbh = int(hgbh)  
  
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
                    new_line = f'{qq}={number}{match.group(2)}\n'  
                    temp_file.write(new_line)  
                    updated = True  
                else:  
                    temp_file.write(line)  
            else:  
                temp_file.write(line)  
  
        # 如果未更新，则添加新行  
        if not updated:  
            temp_file.write(f'\n{qq}={hgbh}\n') 
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
  
def change_txt(csv_path, search_term, m):      
    # 加载CSV文件到pandas DataFrame      
    #df = pd.read_csv(csv_path, header=None)  # 假设没有列名，使用header=None      
    
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
  

def read_txt(qq, filename='qq.txt'):
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
                else:
                    # 如果能转换为整数，同时赋值给str_love
                    str_love = value
                break  # 找到匹配项后退出循环

        # 如果没有找到匹配的qq，在文件末尾添加新条目
        if str_love is None:
            new_line = f'\n{qq}=0'
            file.write(new_line)  # 由于已经处于文件末尾，可以直接写入
            str_love = '0'  # 设置str_love为新添加的数值
            int_love = '0'  # 设置int_love为新添加的数值
            logger.debug('已新增行')

    # 如果int_love仍然为None，表示没有纯数字值被提取，但这在上面的逻辑中不太可能发生
    # 因为即使文本+数字不能转换为整数，str_love也会被设置为文本+数字
    logger.debug('读取好感度完成')
    return int_love, str_love       

def GlobalCompare(filename='qq.txt'):  
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
@bot.on(GroupMessage)
async def bhrkhrt(event: GroupMessage):
    message =str(event.message_chain) 
    qq=str(event.sender.id)
    int_love,str_love=read_txt(qq)
    reply,love=change_txt(csv_path,message,int_love)
    try:
        love = int(love)
    except:
        love = int(0)
    if reply != None:
        await bot.send(event,reply)
    if love != 0:
        update_txt(qq,love)

@bot.on(GroupMessage)
async def sadxchjw(event: GroupMessage):
    if str(event.message_chain) == '我的好感度' or str(event.message_chain) == '我的好感':
        qq2=str(event.sender.id)
        int_love,str_love=read_txt(qq2)
        if str_love != ''or None:
           await bot.send(event,'你的好感度是：\n'+str_love+'\n————————\n(ˉ▽￣～) 切~~')
        else:
           await bot.send(event,'第一次见呢，你的好感度是0 ≡ω≡')     #此语句不一定有效

@bot.on(GroupMessage)
async def dewcfvew(event: GroupMessage):
    global b
    b=str('好♡感♡排♡行\n')
    if str(event.message_chain) =='好感排行':
        qq_list=GlobalCompare  
        for item in qq_list():
            a=str(item)   
            b=b+a+'\n'

        await bot.send(event,b + '--------\n喵呜~~~')

''' 如何实现没思路
@bot.on(GroupMessage)
async def dewcfvew(event: GroupMessage):
    if str(event.message_chain) =='本群好感排行':
'''
try:
       bot.run()
except Exception as e:
        logger.error(e)
        input("按任意键退出")