import os
import asyncio
import logging
from typing import List, Optional
from notebooklm import NotebookLMClient
from app.core.config import get_settings
from app.models.notebook import Notebook, NotebookQuery
from sqlmodel import select
from app.core.db import async_session_maker

logger = logging.getLogger(__name__)
settings = get_settings()

class NotebookService:
    def __init__(self):
        self.storage_path = os.path.join(os.getcwd(), "scratch", "notebooklm_storage.json")
        self.lock = asyncio.Lock()  # Global lock to prevent Google spam bans

    async def interactive_login(self):
        from playwright.async_api import async_playwright
        
        # We run this in a background task to not block the API response
        async def _login_task():
            try:
                async with async_playwright() as p:
                    browser_profile = os.path.join(os.getcwd(), "scratch", "playwright_profile")
                    os.makedirs(browser_profile, exist_ok=True)
                    os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
                    
                    try:
                        context = await p.chromium.launch_persistent_context(
                            user_data_dir=browser_profile,
                            headless=False,
                            args=["--disable-blink-features=AutomationControlled", "--password-store=basic"],
                            ignore_default_args=["--enable-automation"],
                        )
                    except Exception as e:
                        logger.error(f"Playwright failed to launch in non-headless mode (is this a headless server?): {e}")
                        return

                    try:
                        page = context.pages[0] if context.pages else await context.new_page()
                        await page.goto("https://notebooklm.google.com/")
                        
                        # Wait until URL is not the sign-in page, or specifically contains /notebook
                        # NotebookLM redirects to / after login, or /notebook/
                        await page.wait_for_function("() => !window.location.href.includes('accounts.google.com') && document.querySelector('title') && document.querySelector('title').innerText.includes('NotebookLM')", timeout=300000)
                        
                        # Extra wait to ensure cookies are set
                        await asyncio.sleep(3)
                        await context.storage_state(path=self.storage_path)
                        logger.info("Login successful and storage saved.")
                    except Exception as e:
                        logger.error(f"Login timeout or failed during page navigation: {e}")
                    finally:
                        await context.close()
            except Exception as e:
                logger.error(f"Playwright background task failed: {e}")

        # Start task
        asyncio.create_task(_login_task())
        return {"status": "pending", "message": "Browser opened on server. Please complete login."}

    def _ensure_storage(self):
        if not os.path.exists(self.storage_path):
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            raise Exception(f"NotebookLM storage not found at {self.storage_path}. Please use the UI to Login.")

    async def sync_notebooks(self):
        """Sync notebooks from Google to local DB"""
        self._ensure_storage()
        async with self.lock:
            client = await NotebookLMClient.from_storage(self.storage_path)
            async with client:
                remote_notebooks = await client.notebooks.list()
                
                async with async_session_maker() as session:
                    for remote_nb in remote_notebooks:
                        statement = select(Notebook).where(Notebook.external_id == remote_nb.id)
                        result = await session.execute(statement)
                        local_nb = result.scalar_one_or_none()
                        
                        if not local_nb:
                            local_nb = Notebook(
                                external_id=remote_nb.id,
                                title=remote_nb.title
                            )
                            session.add(local_nb)
                        else:
                            local_nb.title = remote_nb.title
                    await session.commit()

    async def create_notebook(self, title: str) -> Notebook:
        self._ensure_storage()
        async with self.lock:
            client = await NotebookLMClient.from_storage(self.storage_path)
            async with client:
                remote_nb = await client.notebooks.create(title)
                
                local_nb = Notebook(
                    external_id=remote_nb.id,
                    title=remote_nb.title
                )
                async with async_session_maker() as session:
                    session.add(local_nb)
                    await session.commit()
                    await session.refresh(local_nb)
                return local_nb

    async def add_source_url(self, notebook_external_id: str, url: str):
        self._ensure_storage()
        async with self.lock:
            client = await NotebookLMClient.from_storage(self.storage_path)
            async with client:
                return await client.sources.add_url(notebook_external_id, url, wait=True)

    async def get_sources(self, notebook_external_id: str) -> List[dict]:
        self._ensure_storage()
        async with self.lock:
            client = await NotebookLMClient.from_storage(self.storage_path)
            async with client:
                sources = await client.sources.list(notebook_external_id)
                return [
                    {
                        "id": src.id,
                        "title": src.title,
                    }
                    for src in sources
                ]

    async def ask_question(self, notebook_external_id: str, question: str, user_id: Optional[str] = None, source: str = "dashboard") -> dict:
        self._ensure_storage()
        
        async with self.lock:
            client = await NotebookLMClient.from_storage(self.storage_path)
            async with client:
                try:
                    result = await client.chat.ask(notebook_external_id, question)
                except Exception as e:
                    logger.error(f"Error calling NotebookLM API: {e}")
                    raise Exception("Failed to get a response from NotebookLM.")
                
                if not result:
                    logger.error("NotebookLM returned an empty result.")
                    raise Exception("NotebookLM returned an empty result.")
                    
                answer = result.answer
                
                if not answer:
                    logger.warning("NotebookLM returned a result with an empty answer.")
                    answer = "No answer was provided by NotebookLM."
                
                # Serialize references
                references = []
                if hasattr(result, 'references') and result.references:
                    for ref in result.references:
                        references.append({
                            "document_id": ref.document_id,
                            "text": getattr(ref, 'cited_text', getattr(ref, 'text', '')),
                            "title": getattr(ref, 'title', f"Source {ref.document_id}")
                        })
                
                # Append references textually to the answer
                if references:
                    answer += "\n\n📚 **Referensi Sumber:**\n"
                    for idx, ref in enumerate(references, 1):
                        answer += f"{idx}. {ref['title']}\n"
                
                # Log to DB
                async with async_session_maker() as session:
                    # Find local notebook id
                    statement = select(Notebook).where(Notebook.external_id == notebook_external_id)
                    db_result = await session.execute(statement)
                    nb = db_result.scalar_one_or_none()
                    
                    if nb:
                        query_log = NotebookQuery(
                            notebook_id=nb.id,
                            user_id=user_id,
                            question=question,
                            answer=answer,
                            source=source
                        )
                        session.add(query_log)
                        await session.commit()
                
                return {
                    "answer": answer,
                    "references": references
                }


notebook_service = NotebookService()
