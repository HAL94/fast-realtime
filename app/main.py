import asyncio
import random

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import redis.asyncio as redis

redis_client = redis.Redis(host='localhost', port=6379, db=0) # Adjust as needed
channel_name = "scores"
scores_sorted_set = 'scores'

user_id = 0
    
app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <div id='redis'>            
        </div>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            } 
            
            var wsu1 = new WebSocket("ws://localhost:8000/ws/u1");
            wsu1.onmessage = function(event) {
                var messages = document.getElementById('redis')  
                const data = JSON.parse(event.data)
                const result = data.result
                console.log("result", result)
                messages.innerHTML = result
            };                           
            
        </script>
    </body>
</html>
"""

@app.get('/')
async def welcome():
    return HTMLResponse(html)


async def subscriber(websocket: WebSocket):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel_name)
    
    try:                        
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"].decode("utf-8")
                print(f'received from pubsub: {data}')
                await websocket.send_text(data)  
    except Exception as e:
        print(f"error at subscriber: {e}")

async def publish(score: int | str): 
    global user_id   
    user_id += 1
    id = f"u{user_id}"
    await redis_client.zadd(scores_sorted_set, {id: score})
    await redis_client.publish(channel_name, '') 
        
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await asyncio.sleep(0.2)
    await redis_client.publish(channel_name, '')
    
    while True:        
        data = await websocket.receive_text()
        print(f"received: {data}")
        await publish(data)
        await websocket.send_text(f"Message text was: {data}")


    

@app.websocket("/ws/u1")
async def websocket_user1_score(websocket: WebSocket):    
    await websocket.accept()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel_name)
    print(f"Subscribed to channel: {channel_name}")       
    try:        
        async for message in pubsub.listen():
            # print(f"Received message: {message}")
            if message["type"] == "message":
                # data = message["data"].decode("utf-8")
                # print(f"Decoded data: {data}")
                data = await redis_client.zrange(scores_sorted_set, 0, -1, withscores=True)
                print("data", data)
                await websocket.send_json({"result": [t[1] for t in data]})
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
    except Exception as e:
        print(f"Websocket error: {e}")
    
    