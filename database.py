
from datetime import datetime, timedelta
import uuid
from pymongo import MongoClient, ReturnDocument
from schemas import MessageData
import redis
import os

R = redis.Redis(
  host=os.getenv("REDIS_HOST"),
  port=int(os.getenv("REDIS_PORT")),
  password=os.getenv("REDIS_PWD"))
# MongoDB URI
MONGODB_URI = os.getenv("MONGODB_URI")

# Synchronous MongoDB client
sync_client = MongoClient(MONGODB_URI)
db = sync_client.get_database("ai-backend")


def get_chat_history(username: str,last_n: int):
    # Synchronous query to MongoDB
    return list(db.chat_history.find({"user_name": username}).sort([("timestamp", -1)]).limit(last_n))

def set_chat_history(userInput: MessageData):
    data = userInput.model_dump()
    data['timestamp'] = datetime.utcnow()
    
    if userInput.id is None:
        # 创建新文档时生成新的 _id
        data['_id'] = str(uuid.uuid4())
    else:
        # 使用提供的 _id 更新现有文档
        data['_id'] = userInput.id

    data.pop("id", None)  # 移除额外的 id 字段

    filter_data = {"_id": data['_id']}
    update_data = {"$set": data}

    result = db.chat_history.find_one_and_update(
        filter_data,
        update_data,
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    return str(result["_id"])



def can_send_daily_message(user_id):
    daily_key = f"daily_count:{user_id}:{datetime.now().date()}"
    current_count = R.incr(daily_key)
    
    if current_count == 1:
        # 第一次增加计数器时设置过期时间
        # 计算从现在到午夜的秒数
        tomorrow = datetime.now().date() + timedelta(days=1)
        midnight = datetime.combine(tomorrow, datetime.min.time())
        seconds_until_midnight = (midnight - datetime.now()).seconds
        R.expire(daily_key, seconds_until_midnight)
    
    if current_count > 20:
        return False  # 超出每日限制
    return True

def get_today_send_msg_count(user_id):
    daily_key = f"daily_count:{user_id}:{datetime.now().date()}"
    current_count = R.get(daily_key)
    max_messages_per_day = 20
    if not current_count:
        return 0
    current_count = int(current_count)
    if current_count > max_messages_per_day:
        return max_messages_per_day
    return current_count

def can_send_30s_message(user_id):
    key_30s = f"30s_count:{user_id}"
    current_count = R.incr(key_30s)
    
    if current_count == 1:
        # 第一次增加计数器时设置过期时间为30秒
        R.expire(key_30s, 30)
    
    if current_count > 3:
        return False  # 超出30秒内限制
    return True
