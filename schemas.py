from pydantic import BaseModel
from typing  import Any, List, Optional

class MessageItem(BaseModel):
    id: int
    content: str
    role: str
    msgType: str


class MessageData(BaseModel):
    id: Optional[Any] = None # id 可以是任何类型
    user_name: str
    message: List[MessageItem]
