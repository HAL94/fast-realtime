import asyncio


from fastapi import FastAPI, WebSocket
import redis.asyncio as redis

redis_client = redis.Redis(host='localhost', port=6379, db=0) # Adjust as needed
channel_name = "scores"
scores_sorted_set = 'scores'

user_id = 0
    
app = FastAPI()

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

    await websocket.send_text("Welcome to your websocket server");
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
    # pubsub = redis_client.pubsub()
    # await pubsub.subscribe(channel_name)
    print(f"Subscribed to channel: {channel_name}")       
    try:        
        # async for message in pubsub.listen():
            # print(f"Received message: {message}")
            # if message["type"] == "message":
                # data = message["data"].decode("utf-8")
                # print(f"Decoded data: {data}")
        data = await redis_client.zrange(scores_sorted_set, 0, -1, withscores=True)        
        await websocket.send_json({"result": [t[1] for t in data]})
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
    except Exception as e:
        print(f"Websocket error: {e}")
    
    