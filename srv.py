from io import BytesIO
from pathlib import Path
import re
import time

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from src.grabcraft import get_definition
from src.litematic import grabcraft2region
from src.stats_db import StatsDB


app = FastAPI()


def store_request(url: str, request: Request):
    user_agent = request.headers.get('User-Agent', '')

    browser = 'Unknown'
    if 'Firefox' in user_agent:
        browser = 'Firefox'
    elif 'Chrome' in user_agent:
        browser = 'Chrome'
    elif 'Safari' in user_agent:
        browser = 'Safari'
    elif 'MSIE' in user_agent or 'Trident' in user_agent:
        browser = 'Internet Explorer'

    operating_system = 'Unknown'
    if 'Windows' in user_agent:
        operating_system = 'Windows'
    elif 'Macintosh' in user_agent:
        operating_system = 'MacOS'
    elif 'X11' in user_agent:
        operating_system = 'Linux'
    elif 'Android' in user_agent:
        operating_system = 'Android'

    with StatsDB(str(Path(__file__).parent.joinpath('db', 'stats.db'))) as stats_db:
        stats_db.track_request(
            url=url,
            ip_address=request.client.host,
            timestamp=int(round(time.time() * 1000)),
            browser=browser,
            operating_system=operating_system,
            user_agent=user_agent,
            referrer=request.headers.get('Referer', '')
        )


@app.get('/api/convert')
async def g2l(grabcraft_url: str, request: Request, response: Response):
    if not re.match(r'^https?://[^.]+?\.?grabcraft\.com/', grabcraft_url):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Invalid URL'}

    definition = get_definition(grabcraft_url)
    region = grabcraft2region(definition)
    output = BytesIO()
    region \
        .as_schematic(name=definition.title, author=definition.author) \
        .save(output)
    output.seek(0)

    store_request(grabcraft_url, request)

    return StreamingResponse(
        content=output,
        headers={'Content-Disposition': f'attachment; filename="{definition.title}.litematic"'}
    )

app.mount('/', StaticFiles(directory=Path(__file__).parent.joinpath("web", "static"), html=True), name="static")
