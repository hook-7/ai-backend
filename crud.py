
import os
from fastapi.encoders import jsonable_encoder
from database import set_chat_history

from schemas import MessageData, MessageItem
from typing import List, Dict
from transformers import AutoTokenizer
from openai import OpenAI

client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENAI_API_KEY"),
)


def send_ai_chat_msg(input_data: MessageData):
    json_compatible_content = jsonable_encoder(input_data.message)
    json_compatible_content = reduce_tokens_from_middle(json_compatible_content, 8192)

    # Prepare messages for the API, ensuring only expected fields are included
    api_messages = [{
        "role": msg["role"],
        "content": msg["content"]
    } for msg in json_compatible_content if "role" in msg and "content" in msg]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=api_messages,
    )
    
    # Instantiate MessageItem with all required fields, including 'id' and 'msgType'
    message_item = MessageItem(
        id=0,  # or another appropriate value based on your application's logic
        content=completion.choices[0].message.content,  
        role=completion.choices[0].message.role,  
        msgType="received"  # Assuming 'received' is a valid value for your model
    )
    input_data.message.append(message_item)

    # Serialize the completion and perform further processing as needed
    completion_data = completion.model_dump()
    completion_data["_id"] = set_chat_history(input_data)

    return completion_data



def calculate_total_tokens(data: List[Dict]) -> int:
    """
    计算给定数据中所有 "content" 字段的总 token 数量。

    :param data: 包含多个字典的列表，每个字典至少包含一个 "content" 字段。
    :return: 总 token 数量。
    """
    model_name = "bert-base-multilingual-cased"
    # 加载预训练的 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # 计算 token 总数
    total_tokens = sum(len(tokenizer.tokenize(item["content"])) for item in data if "content" in item)

    return total_tokens



def reduce_tokens_from_middle(data: List[Dict], max_tokens: int) -> List[Dict]:
    """
    调整数据列表，从中间开始删除内容，以确保总 token 数量不超过最大限制。

    :param data: 包含多个字典的列表，每个字典至少包含一个 "content" 字段。
    :param max_tokens: 允许的最大 token 数量。
    :return: 调整后的数据列表。
    """
  # tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
    tokenizer = AutoTokenizer.from_pretrained("./.tokenizer/")
    # tokenizer.save_pretrained("./.tokenizer/")

    # 计算总 token 数量
    total_tokens = sum(len(tokenizer.tokenize(item["content"])) for item in data)

    if total_tokens <= max_tokens:
        return data  # 如果不超过限制，直接返回原数据

    # 初始化左右索引
    left_index, right_index = 0, len(data) - 1

    # 循环删除直到满足 token 数量限制
    while total_tokens > max_tokens and left_index <= right_index:
        # 计算左右两边的 token 数量
        left_tokens = len(tokenizer.tokenize(data[left_index]["content"])) if left_index <= right_index else 0
        right_tokens = len(tokenizer.tokenize(data[right_index]["content"])) if right_index >= left_index else 0

        # 优先从 token 数较少的一边删除
        if left_tokens < right_tokens:
            total_tokens -= left_tokens
            left_index += 1
        else:
            total_tokens -= right_tokens
            right_index -= 1

    # 根据确定的索引删除数据中间的部分
    # 注意：为了简化，这里我们删除从 left_index 到 right_index 的所有内容
    del data[left_index:right_index + 1]

    return data