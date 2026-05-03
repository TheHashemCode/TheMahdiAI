from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import uuid
from pydantic import BaseModel

from app.core.db import get_session
from app.models.notebook import Notebook, NotebookQuery
from app.services.notebook_service import notebook_service

router = APIRouter()

class NotebookCreate(BaseModel):
    title: str

class SourceAdd(BaseModel):
    url: str

class QuestionAsk(BaseModel):
    question: str
    user_id: Optional[str] = None

@router.get("/")
async def list_notebooks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Notebook).order_by(Notebook.created_at.desc()))
    return result.scalars().all()

@router.post("/login")
async def trigger_login():
    try:
        return await notebook_service.interactive_login()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import logging
logger = logging.getLogger(__name__)

@router.post("/sync")
async def sync_notebooks():
    try:
        await notebook_service.sync_notebooks()
        return {"status": "success", "message": "Notebooks synced from Google"}
    except Exception as e:
        logger.error(f"Error syncing notebooks: {repr(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/")
async def create_notebook(data: NotebookCreate):
    try:
        nb = await notebook_service.create_notebook(data.title)
        return nb
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{external_id}/sources")
async def add_source(external_id: str, data: SourceAdd):
    try:
        result = await notebook_service.add_source_url(external_id, data.url)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{external_id}/sources")
async def list_sources(external_id: str):
    try:
        sources = await notebook_service.get_sources(external_id)
        return sources
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{external_id}/ask")
async def ask_notebook(external_id: str, data: QuestionAsk):
    try:
        response_data = await notebook_service.ask_question(
            external_id, 
            data.question, 
            user_id=data.user_id,
            source="dashboard"
        )
        return response_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history")
async def get_history(session: AsyncSession = Depends(get_session)):
    # Join with Notebook to get titles
    stmt = select(NotebookQuery, Notebook.title).join(Notebook).order_by(NotebookQuery.created_at.desc()).limit(100)
    result = await session.execute(stmt)
    history = []
    for query, title in result:
        history.append({
            "id": query.id,
            "notebook_title": title,
            "question": query.question,
            "answer": query.answer,
            "source": query.source,
            "created_at": query.created_at
        })
    return history
