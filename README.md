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
**LoveYou是一个可高度自定义的词库+好感度系统插件**
**运行本项目，你需要确保你拥有至少300MB的空闲内存**
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
 * 查询好感*QQ*、查询好感*@*
 * 好感排行
 * 本群好感排行
 * /code alias *YourCode* ：设置QQ别名。使用被记录在./data/code_users.txt
 * /code love *YourCode* ：设置文本好感。使用被记录在./data/code_users.txt
 
 ### 主人指令
**群聊**
* /set(del) senior *QQ*：设置(取消)本群词库高管，其中*QQ*为高管QQ号
* /set(del) admin *QQ*：设置(取消)本群词库管理，其中*QQ*为管理QQ号

**私聊**
* /encode alias *int_number*：生成QQ别名的code，其中*int_number*为生成数量。可在./data/alias_code.txt查看code
* /encode love *int_number*：生成文本好感的code，其中*int_number*为生成数量。可在./data/love_code.txt查看code
### 词库指令
 **高管指令**
* /set(del) admin *QQ*：设置(取消)本群词库管理，其中*QQ*为管理QQ号

**管理指令**
* 精确问 *Question* *Answer*：为本群添加一组回复，请注意整个指令中第二个空格是*Question*和*Answer*的切分点
* 删除 *Question*：删除对应*Question*，其中*Question*的所有对应项均会被删除
****
## 词库编辑
#### reply.csv
**不支持热重载**
按照下表格式填写reply.csv，它是全局生效的
|  消息   |  回复   |    好感范围 |    触发范围 |
| :-: | :-: | :-: | :-: |
|  test   |   123[pic=atri.jpg][cut]456[pic=v.jpg]  |  (-10,10)   | (-10,10)    |
|   quick_RL  |  RL%apple%R:0.2,L:5!%banana%L:-4,R:0.4!%monkey%R:2.0!   |   (-10,10)  |  (-10,10)   |
**对于该表的解释**
* 好感范围：本行触发时，从随机范围内随机取一个整数值作为好感变化量。默认值为**config.ini**下common_love所对应的区间。特别地，你可以在回复中使用<mark>[vary]</mark>来指代好感变化量，这将使得变化量可见
* 触发范围：只有当触发者的好感在本范围内，本行才会触发。默认无范围
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

**实例**：效果同test行
![test](https://img2.imgtp.com/2024/05/25/S0QryhTK.PNG "test示例" =1100x)
#### 群聊词库
**群聊词库是全局词库的阉割**
* 好感范围默认值为0，而非common_love
* 不支持指令设置 好感范围 和 触发范围，尽管代码支持读取与运算
* 不支持指令添加[pic=' ']，尽管代码支持发送
* 通过quick_RL方法设置的L值强制变更为0

**如果你真的需要以上功能**：
* 在./data/group/下找到对应csv，手动编辑
* 将图片放置于./data/pic/group/下
* 无论如何，quick_RL的L值无法恢复
****
## 好感度系统
**好感度来源**
* 词库
* 消息中包含<mark>bot_name</mark>或<mark>@bot</mark>时，程序会分析情感偏向并给出一个[-10,10]之间的整数值作为好感变化量

**CG**
这是一个真正可高度自定义的模块
仅当消息包含<mark>bot_name</mark>时进行判断
每个QQ每日最多触发一次判断，早上9点重置
* 仅支持发送图片，请将图片放置于./data/CG/下（.jpg or .png）
* baseline：触发CG回复所要求的最低好感度
* rate：CG发送概率
详见**config.ini**

**好感度等级**
如要启用本功能，请设置**config.ini**中enable=True
共分为5个等级
在**config.ini**设置每级所囊括的好感区间（例：lv1=-999,-50）
在**config.ini**设置每级查询好感度时所回复的特殊回复
**变量支持：见词库编辑**
****
## 进阶使用
**quick_RL方法**
这是一个略显繁琐的回复方法，但它在某种意义上是简洁的
以下表为例
| 消息    |   回复  |  好感范围   |  触发范围   |
| :-: | :-: | :-: | :-: |
|  quick_RL   |  RL%apple%R:0.2,L:5!%banana%L:-4,R:0.4!%monkey%R:2.0!   |  (-99,9999)   |    (114514,1919810) |
<br />
<mark>**！重要！**</mark>你需要在回复的最开头用**RL**声明你将要使用quick_RL方法，用于声明的**RL**将在随后的处理中被抛弃<br />
它可以被这么解读：<br />
**%这里是每一条回复%R：这里是本回复权重；L：这里是本回复对应的好感度变化**<br />
在quick_RL方法中，R和L均为可选项，R默认为1.0，L默认为0。R和L的顺序是不严格的<br />
当quick_RL行被触发时，会在回复中进行新一轮的加权随机选择<br />
只有% %之间的内容会被认为是回复<br />
每一条回复和它的参数与后一条回复应当存在！作为分割，！的全半角输入是不严格的<br />
被随机中的回复所携带的L会被认为是好感变化值，这意味着整个语句的 好感范围 是**没有意义**的，而 触发范围 仍然**具有意义**