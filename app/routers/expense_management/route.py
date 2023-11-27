import json
from typing import List
import asyncio

from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from app.database.sqlalchemy import Session
from app.routers.expense_management.request_model import AddExpense
from app.schemas.EM import Expense

from app.routers.expense_management.connect_manager import ConnectionManager

load_dotenv()
app = FastAPI()


expense_router = APIRouter(tags=["Expense"], prefix="/expense")


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
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8081/expense/ws");
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
        </script>
    </body>
</html>
"""


manager = ConnectionManager()
TIMEOUT = 30000


@expense_router.get("/home")
async def expense_home():
    return HTMLResponse(html)


@expense_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    print("websocket connected")
    try:
        await manager.send_personal_message(
            f"{client_id} successfully connected", websocket
        )
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=TIMEOUT)
                await manager.broadcast(f"Client #{client_id} says: {data}")
            except asyncio.TimeoutError:
                print("close")
                await manager.disconnect(websocket)
                break
    except WebSocketDisconnect:
        print("close_2")
        manager.disconnect(websocket)


@expense_router.get("/test")
async def test():
    await manager.send_personal_message("test")
    return {"test": "test"}


@expense_router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_expense(expense: AddExpense):
    # append new expense to database
    with Session() as session:
        new_expense = Expense(
            expense_id=expense.expense_id,
            expense_name=expense.expense_name,
            expense_type=expense.expense_type,
            expense_amount=expense.expense_amount,
            expense_time=expense.expense_time,
        )
        session.add(new_expense)
        session.commit()

        # broadcast new expense to all clients
        expense_info = json.dumps(
            {
                "expense_id": str(expense.expense_id),
                "expense_name": expense.expense_name,
                "expense_type": expense.expense_type,
                "expense_amount": expense.expense_amount,
                "expense_time": expense.expense_time,
            }
        )
    print("send")
    await manager.broadcast(expense_info)

    return {"expense": "ok"}
