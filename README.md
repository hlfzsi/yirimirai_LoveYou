本readme适用版本 : v1.40-v1.50
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
~~**运行本项目，你需要确保你拥有至少300MB的空闲内存**
从v1.42开始，项目需要接近500MB的内存。希望有人可以看一看如何优化（哭）~~
~~**内存占用可使用虚拟内存代替**~~
<br>
**在v1.50，内存占用降低至150MB左右，常驻内存为100MB**
<br>
以下三点是本插件的开发宗旨
* 词库的编辑是简易、高效且可视化的
* 好感度系统是完全兼容词库且高效的
* 项目是灵动的，而非死气沉沉的
****

## 项目指令
斜体为需输入的变量
### 用户指令
 **群聊**
 * 我的好感、我的好感度
 * 好感排行
 * 本群好感排行
 * /code alias *YourCode* ：设置QQ别名。使用被记录在./data/code_users.txt
 * /code love *YourCode* ：设置文本好感。使用被记录在./data/code_users.txt
 *  <small><small>v1.42加入</small></small>/code pic *YourCode* ：设置图片好感回复。使用被记录在./data/code_users.txt
 ### 主人指令
**群聊**
* /set(del) senior *QQ*：设置(取消)本群词库高管，其中*QQ*为高管QQ号
* /set(del) admin *QQ*：设置(取消)本群词库管理，其中*QQ*为管理QQ号

**私聊**
* /encode alias *int_number*：生成QQ别名的code，其中*int_number*为生成数量。可在./data/alias_code.txt查看code
* /encode love *int_number*：生成文本好感的code，其中*int_number*为生成数量。可在./data/love_code.txt查看code
*  <small><small>v1.42加入</small></small>/encode pic *int_number*：生成文本好感的code，其中*int_number*为生成数量。可在./data/pic_code.txt查看code 
### 词库指令
 **高管指令**
* /set(del) admin *QQ*：设置(取消)本群词库管理，其中*QQ*为管理QQ号
*  <small><small>v1.42加入</small></small>/(un)lock *行号*：解锁/锁定对应行号，支持列表，以空格分隔

**管理指令**
* <small><small>v1.42更新</small></small>精确(模糊)问 *Question* *Answer*：为本群添加一组回复，请注意整个指令中第二个空格是*Question*和*Answer*的切分点
* 删除 *Question*：删除对应*Question*，其中*Question*的所有对应项均会被删除
* <small><small>v1.42加入</small></small>查询 *Question*：返回所有对应项的行号
* <small><small>v1.42加入</small></small>/dr *行号*：删除对应行号，支持列表，以空格分隔
* <small><small>v1.42加入</small></small>/info *行号*：返回对应行号回复详细信息
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
* [pic=' ']：发送图片。请将要发送的图片置于 ./data/pic/ 下。每条消息仅支持一张图片。只要填入文件名即可，包括后缀
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
* ~~不支持指令添加[pic=' ']，尽管代码支持发送~~ 从v1.42开始，图片已默认支持
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
* 特别地，bot有0.6%的概率进行群聊回复及好感运算

**CG**
这是一个真正可高度自定义的模块<br>
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
你应当向LoveYou发送一个json，它的**内容**及**返回**按顺序如下
| type    | qq    |   love  |  return   |
| :-: | :-: | :-: |:-: |
|  这代表你要调用的函数   |  目标QQ   |    好感变化 | 正常返回的格式  |
|   get_love  |  Any   |  json中请不要包含love键值对   |  数值好感&#124;&#124;&#124;文本好感  |
|   change_love  |  Any   |  int   |  DONE  |
<br>
如果调用失败，LoveYou会返回错误的原因。若调用成功而LoveYou内部函数执行失败，LoveYou会返回Fail<br>
LoveYou的默认ws端口为8686