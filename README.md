本readme适用版本 : v1.40-v1.51
# 免责声明
### 本项目禁止用于包括但不限于：违法犯罪、灰色地带等一切有背于社会主义核心价值观的行为。
### 下载本插件或源码则默认同意以上内容
****
## 鸣谢
* [YiriMirai](https://github.com/YiriMiraiProject/YiriMirai)一个轻量级、低耦合的基于 mirai-api-http 的 Python SDK。
* [mirai](https://github.com/mamoe/mirai)——高效率 QQ 机器人支持库
* [mirai-api-http](https://github.com/project-mirai/mirai-api-http)——提供HTTP API供所有语言使用mirai。
****
## 项目简介
**LoveYou是一个高性能的、可高度自定义的词库+好感度系统插件**
<br>
**在v1.50及以后，内存占用降低至170MB左右**
<br>
以下三点是本插件的开发宗旨
* 词库的编辑是简易、高效且可视化的
* 好感度系统是完全兼容词库且高效的
* 项目是灵动的，而非死气沉沉的
<br>
本项目release包性能表现：已知2w行的词库可瞬间回复。[测试用词库](https://github.com/hlfzsi/yirimirai_LoveYou/blob/main/example/reply.csv)
****
## 快速上手
本项目仅支持64位系统<br>
首先，请正确配置mirai-api-http<br>
[mirai-api-http参考配置](https://github.com/avilliai/wReply/blob/master/setting.yml)
需要注意，本项目仅支持正向ws<br>
之后，你需要确认config.ini填写无误


`````
请勿直接复制本config.ini
[bot]如果你按照mirai-api-http参考配置进行部署，则无需修改verify_key、host、port
bot_qq = bot的QQ号
verify_key = 1234567890
host = 127.0.0.1
port = 23456
[random_CG]
baseline=触发CG的最低好感要求
rate=0.02触发CG的概率（0-1.00）
[others]
ws=True是否启用LoveYou自带的ws，默认启用
ws_port=8686 LoveYou的ws端口，默认为8686
bot_name=bot的名称
master=bot主人的QQ号
search_love_reply=查询好感 指令的回复格式
tank_enable=True是否启用幻影坦克
[csv]
common_love=-1,1  reply.csv的默认好感变化范围
[ai]
@_react=True是否启用@对策
model=调用的模型名称
;model可填qingyunke或百度大模型（需要自己获取）。若使用百度模型，请填写role、API_Key、Secret_Key、memory
role=ai人设，支持[sender][intlove][time]变量
API_Key=
Secret_Key=
memory=True是否启用记忆功能
[lv]
enable=True是否启用好感等级机制
;通用：\n为换行，[qq]为QQ号，[sender]为群名片，[love]为好感度，[intlove]为数值好感度，[bot]为bot名称
;对于csv，[vary]为本次回复数值好感度变化
之后的reply均为不同等级的 我的好感度  指令回复格式
lv1=-999,-50
lv1_reply=


lv2=-50,50
lv2_reply=


lv3=50,200
lv3_reply=

lv4=200,1000
lv4_reply=

lv5=1000,9999
lv5_reply=
`````

1.**Windows**<br>
 下载最新的[release](https://github.com/hlfzsi/yirimirai_LoveYou/releases)，解压，填写config.ini，编辑你的reply.csv，启动exe即可<br>
2.**Linux**
下载最新的[release](https://github.com/hlfzsi/yirimirai_LoveYou/releases)，解压，填写config.ini，编辑你的reply.csv，尝试使用wine启动exe<br>
如无法启动，请尝试[Issues#1](https://github.com/hlfzsi/yirimirai_LoveYou/issues/1)中的方法<br>
欢迎提供Linux上的打包
****
## 项目指令
斜体为需输入的变量
### 用户指令
 **群聊**
 * 我的好感、我的好感度
 * 好感排行
 * (v1.51)我的排名
 * (Unknown)好人榜
 * (v1.51)/clear：清理对话记忆
 * 本群好感排行
 * (v1.50)/gtank：生成幻影坦克
 * /code alias *YourCode* ：设置QQ别名。使用被记录在./data/code_users.txt
 * /code love *YourCode* ：设置文本好感。使用被记录在./data/code_users.txt
 * (v1.42)/code pic *YourCode* ：设置图片好感回复。使用被记录在./data/code_users.txt
 ### 主人指令
**群聊**
* /set(del) senior *QQ*：设置(取消)本群词库高管，其中*QQ*为高管QQ号
* /set(del) admin *QQ*：设置(取消)本群词库管理，其中*QQ*为管理QQ号

**私聊**
* /encode alias *int_number*：生成QQ别名的code，其中*int_number*为生成数量。可在./data/alias_code.txt查看code
* /encode love *int_number*：生成文本好感的code，其中*int_number*为生成数量。可在./data/love_code.txt查看code
*  (v1.42)/encode pic *int_number*：生成文本好感的code，其中*int_number*为生成数量。可在./data/pic_code.txt查看code 
### 词库指令
 **高管指令**
* /set(del) admin *QQ*：设置(取消)本群词库管理，其中*QQ*为管理QQ号
*  (v1.42)/(un)lock *行号*：解锁/锁定对应行号，支持列表，以空格分隔

**管理指令**
* (v1.42更新)精确(模糊)问 *Question* *Answer*：为本群添加一组回复，请注意整个指令中第二个空格是*Question*和*Answer*的切分点
* 删除 *Question*：删除对应*Question*，其中*Question*的所有对应项均会被删除
* (v1.42)查询 *Question*：返回所有对应项的行号
* (v1.42)/dr *行号*：删除对应行号，支持列表，以空格分隔
* (v1.42)/info *行号*：返回对应行号回复详细信息
****
## 词库编辑
#### reply.csv
**不支持热重载**<br>
**需要注意，所有词库均以utf-8编码存储读取。这在Excel中往往表现为乱码，请自行百度解决**<br>
按照下表格式填写reply.csv，它是全局生效的
|  消息   |  回复   |    好感范围 |    触发范围 |类型  |
| :-: | :-: | :-: | :-: |:-: |
|  test   |   123[pic=atri.jpg][cut]456[pic=v.jpg]  |  (-10,10)   | (-10,10)    | 1 |
|   quick_RL  |  RL%apple%R:0.2,L:5!%banana%L:-4,R:0.4!%monkey%R:2.0!   |   (-10,10)  |  (-10,10)   |2  |

**对于该表的解释**
* 好感范围：本行触发时，从随机范围内随机取一个整数值作为好感变化量。默认值为**config.ini**下common_love所对应的区间。特别地，你可以在回复中使用[vary]来指代好感变化量，这将使得变化量可见
* 触发范围：只有当触发者的好感在本范围内，本行才会触发。默认无范围
* 类型：可不填。1代表精准匹配，2代表模糊匹配，不填默认精准匹配。
* [pic=]：发送图片。请将要发送的图片置于 ./data/pic/ 下。每条消息仅支持一张图片。只要填入文件名即可，包括后缀
* [cut]：回复切割。将一次回复切分为多次回复。使用本方法可实现一次触发可发送多张图片
* quick_RL行：本行可实现权重选择，使用较为复杂，详见**进阶使用**

**此外，在消息和回复列中，你可以使用如下变量：**
* \n：换行
* [qq]：触发者QQ号
* [sender]：触发者群名片
* [love]：触发者好感度
* [intlove]：触发者好感度（不包括文本好感）
* [bot]：bot名称，在config.ini中编辑

**上述变量（[vary]除外）在好感回复中也适用；全部变量在群聊词库中适用**
**在模糊匹配中，你还可以使用以下插件**
* [pos]：情感偏向为正时回复
* [nag]：情感偏向为负时回复


#### 群聊词库
**群聊词库是全局词库的阉割**
* 好感范围默认值为0，而非common_love
* 不支持指令设置 好感范围 和 触发范围，尽管代码支持读取与运算
* (**v1.42之前**)不支持指令添加[pic=]，尽管代码支持发送
* 通过quick_RL方法设置的L值强制变更为0
* 模糊匹配的插件仍然是受到支持的

**如果你真的需要以上功能**：
* 在./data/group/下找到对应csv，手动编辑
* 将图片放置于./data/pic/group/下
* 无论如何，quick_RL的L值无法恢复
****
## 好感度系统
**好感度来源**
* 词库
* 消息中包含bot_name或@bot时，程序会分析情感偏向并给出一个[-10,10]之间的整数值作为好感变化量
* 特别地，bot有0.4%的概率进行群聊回复及好感运算

**CG**
仅当消息包含bot_name时进行判断<br>
每个QQ每日最多触发一次判断，早上9点重置
* 仅支持发送图片，请将图片放置于./data/CG/下（.jpg or .png）
* baseline：触发CG回复所要求的最低好感度
* rate：CG发送概率
详见**config.ini**

**好感度等级**
如要启用本功能，请设置**config.ini**中enable=True<br>
共分为5个等级<br>
在**config.ini**设置每级所囊括的好感区间（例：lv1=-999,-50）<br>
在**config.ini**设置每级查询好感度时所回复的特殊回复<br>
**变量支持：见词库编辑**
****
## 进阶使用
**quick_RL方法**
这是一个略显繁琐的回复方法，但它在某种意义上是简洁的
以下表为例
| 消息    |   回复  |  好感范围   |  触发范围   |
| :-: | :-: | :-: | :-: |
|  quick_RL   |  RL%apple%R:0.2,L:5!%banana%L:-4,R:0.4!%monkey%R:2.0!   |  (-99,9999)   |    (114514,1919810) |


**重要**你需要在回复的最开头用**RL**声明你将要使用quick_RL方法，用于声明的**RL**将在随后的处理中被抛弃<br>
它可以被这么解读：<br>
**%这里是每一条回复%R：这里是本回复权重；L：这里是本回复对应的好感度变化**<br>
在quick_RL方法中，R和L均为可选项，R默认为1.0，L默认为0。R和L的顺序是不严格的<br>
当quick_RL行被触发时，会在回复中进行新一轮的加权随机选择<br>
只有% %之间的内容会被认为是回复<br>
每一条回复和它的参数与后一条回复应当存在！作为分割，！的全半角输入是不严格的<br>
被随机中的回复所携带的L会被认为是好感变化值，这意味着整个语句的 好感范围 是**没有意义**的，而 触发范围 仍然**具有意义**
<br>
<small><small>v1.41加入</small></small> **websockets支持**
本项目提供ws方式获得用户好感度、变更用户好感度。<br>
editor.py是一个使用例<br>
要使用LoveYou的ws，请遵循以下简单的规范：<br>
你应当向LoveYou发送一个json，它的部分**内容**及**返回**按顺序如下
| type    | qq    |   love  |  return   |
| :-: | :-: | :-: |:-: |
|  这代表你要调用的函数   |  目标QQ   |    好感变化 | 正常返回的格式  |
|   get_love  |  Any   |  json中请不要包含love键值对   |  数值好感&#124;&#124;&#124;文本好感  |
|   change_love  |  Any   |  int   |  DONE  |
<br>
如果调用失败，LoveYou会返回错误的原因。若调用成功而LoveYou内部函数执行失败，LoveYou会返回Fail<br>
LoveYou的默认ws端口为8686<br>

****
## 基于本项目的Websockets进行开发
简要的接口介绍（type+所需要的传入变量）
1. get_love : 获得对应QQ好感度<br>qq：QQ号<br>
2. change_love ： 修改对应QQ好感度（加法）<br>qq：QQ号<br>love：变更好感度，要求可转换为int类型<br>
3. get_lv ： 获得对应QQ好感等级<br>qq：QQ号<br>
4. get_rank ： 获得对应QQ好感排名<br>qq：QQ号<br>
5. isAdmin ： 检查QQ是否为LoveYou中注册过的特定群管理组成员<br>groupid：群号<br>qq：QQ号<br>
6. silence ： 沉默/启用 LoveYou的词库<br>qq：True沉默或者False解除沉默<br>
7. love_score ： 对文本进行情感分析，返回一个经过处理的好感变化值<br>text：需要分析的文本<br>
#### json示例
变量的存在与否以及存在顺序都是严格的


`````
{  
  "type": "get_love",
  "qq": "123456789"  
}
`````

`````
{  
  "type": "isAdmin",
  "groupid":"123456789",
  "qq":"123456789"
}
`````


#### 返回示例
序号与接口介绍序号一一对应<br>其中，{   }内容为你需要的返回值，{   }在真实返回中不存在<br>如果调用错误，LoveYou会返回错误原因。若调用成功而LoveYou内部函数错误，会返回Fail
1. {int_love}|||{str_love}<br>str_love为int_love加上用户好感后缀<br>
2. DONE
3. {level}<br>1-5为正常返回结果<br>0代表好感超出好感等级范围且好感<0，6代表好感超出好感等级范围且好感>=0<br>若好感等级未启用，则返回-1<br>
4. {rank}|{total}<br>rank为用户排名，total为总排名数<br>
5. {admin?}<br>权限等级：high > common > False，其中，False代表无权限<br>
6. Success
7. {intlove}<br>返回经过处理的好感度变化值，但实际上这一变化值并没有作用于任何QQ