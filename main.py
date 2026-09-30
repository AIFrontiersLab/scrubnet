import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="WebScraper MVP")

class ScrapeRequest(BaseModel):
    url: str = Field(..., description="URL to scrape")
    max_length: int = Field(default=1000, description="Max characters to return")

class ScrapeResponse(BaseModel):
    success: bool
    title: Optional[str] = None
    content: Optional[str] = None
    error: Optional[str] = None

def extract_text(html: str) -> tuple[str, str]:
    title = "Untitled"
    content = ""
    if '<title>' in html:
        start = html.find('<title>') + 7
        end = html.find('</title>')
        if end > start:
            title = html[start:end].strip()
    if '<body>' in html:
        start = html.find('<body>') + 6
        end = html.find('</body>')
        if end > start:
            body = html[start:end]
            content = body.replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '')
            import re
            content = re.sub(r'<[^>]+>', '', content)
    return title, content

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(request: ScrapeRequest):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(request.url, timeout=5.0)
            resp.raise_for_status()
            title, content = extract_text(resp.text)
            return ScrapeResponse(
                success=True,
                title=title,
                content=content[:request.max_length]
            )
    except httpx.RequestError as e:
        return ScrapeResponse(success=False, error=str(e))
    except Exception as e:
        return ScrapeResponse(success=False, error=str(e))

def demo():
    print("Demo: Running local server...")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)