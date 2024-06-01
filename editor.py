import asyncio  
import websockets  
import json 
import time
uri=str(input('请输入IP:端口\n'))
uri='ws://'+uri+'/ws'
print('函数名\nget_love\nchange_love')
type=str(input('请输入函数类型\n'))
qq=str(input('请输入目标QQ\n'))
love=str(input('请输入变更的好感(0为查询)\n'))
if love!='0':
   data = {  
    "type": type,  
    "qq": qq,  
    "love": love 
   }  
else:
   data = {  
    "type": type,  
    "qq": qq
   }  

json_string = json.dumps(data)  
async def client(uri):  
  try:
    async with websockets.connect(uri) as websocket:  
        await websocket.send(json_string)  
        response = await websocket.recv()  
        print(f"Received: {response}") 
        time.sleep(15)
  except:
      print(f"error")
      time.sleep(5)
   
asyncio.run(client(uri))