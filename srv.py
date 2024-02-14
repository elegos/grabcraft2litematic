from io import BytesIO
from pathlib import Path
import re

from fastapi import FastAPI, Response, status
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from grabcraft import get_definition
from litematic import grabcraft2region


app = FastAPI()

@app.get('/api/convert')
async def g2l(grabcraft_url: str, response: Response):
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

    return StreamingResponse(
        content=output,
        headers={'Content-Disposition': f'attachment; filename="{definition.title}.litematic"'}
    )

app.mount('/', StaticFiles(directory=Path(__file__).parent.joinpath("web", "static"), html=True), name="static")
