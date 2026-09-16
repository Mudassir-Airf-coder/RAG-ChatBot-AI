import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings
from app.exceptions import NotFoundError
from app.storage import (
    create_chat as storage_create_chat,
    delete_chat as storage_delete_chat,
    get_chat,
    get_messages_by_chat,
    list_chats,
)

router = APIRouter(prefix="/api/v1/chats", tags=["chats"])


class CreateChatRequest(BaseModel):
    title: str = "New chat"


class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: str


class ChatsListResponse(BaseModel):
    chats: list[dict]


class MessagesResponse(BaseModel):
    chat_id: str
    messages: list[dict]


@router.get("", response_model=ChatsListResponse)
async def list_all_chats() -> ChatsListResponse:
    return ChatsListResponse(chats=list_chats(settings.sqlite_path))


@router.post("", response_model=ChatResponse, status_code=201)
async def create_new_chat(request: CreateChatRequest) -> ChatResponse:
    chat_id = f"chat_{uuid.uuid4().hex[:12]}"
    chat = storage_create_chat(chat_id, request.title, settings.sqlite_path)
    return ChatResponse(**chat)


@router.get("/{id}/messages", response_model=MessagesResponse)
async def get_chat_messages(id: str) -> MessagesResponse:
    chat = get_chat(id, settings.sqlite_path)
    if not chat:
        raise NotFoundError(f"Chat {id} not found")
    msgs = get_messages_by_chat(id, settings.sqlite_path)
    return MessagesResponse(chat_id=id, messages=msgs)


@router.delete("/{id}", status_code=204)
async def delete_chat_by_id(id: str) -> None:
    chat = get_chat(id, settings.sqlite_path)
    if not chat:
        raise NotFoundError(f"Chat {id} not found")
    storage_delete_chat(id, settings.sqlite_path)
