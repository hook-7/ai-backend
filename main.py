from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import crud, schemas
from database import can_send_30s_message, can_send_daily_message, get_chat_history, get_today_send_msg_count
from starlette.exceptions import HTTPException as StarletteHTTPException



# docker run --name test -d -p 8000:8000 -v $(pwd)/.env:/app/.env war7ng/aibackend:1
# uvicorn main:app --reload --host "0.0.0.0" --port 8001

app = FastAPI()

app.mount("/web", StaticFiles(directory="web/dist", html=True), name="web")

@app.get("/")
def read_root():
    return RedirectResponse(url='/web')

@app.post("/get_ai_chat_response")
async def get_ai_chat_response(messageData: schemas.MessageData):
    if not can_send_daily_message(messageData.user_name):
        raise HTTPException(status_code=401, detail="Exceeded daily message limit.")
    if not can_send_30s_message(messageData.user_name):
        raise HTTPException(status_code=401, detail="Exceeded message rate limit (3 messages per 30 seconds).")
    return  crud.send_ai_chat_msg(messageData)

@app.get("/get_user_chat_history/{username}/{last_n}")
async def get_user_chat_history(username: str,last_n:int = 10):
    return get_chat_history(username,last_n)

@app.get("/get_chat_status_today/{user_name}")
async def get_chat_status_today(user_name: str):
    # Logic to get chat status of today
    return get_today_send_msg_count(user_name)

# @app.exception_handler(StarletteHTTPException)
# async def not_found_exception_handler(request: Request, exc: StarletteHTTPException):
#     if exc.status_code == 404 and request.method == "GET":
#         # 返回 index.html
#         return FileResponse('dist/index.html')
#     # 对于其他情况，重新抛出异常，让 FastAPI 使用默认的异常处理机制
#     raise exc
