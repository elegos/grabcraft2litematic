from dataclasses import dataclass
import json
from pathlib import Path
import re
import os

import requests

from common import Coordinates, GenericDefinition

@dataclass
class GrabcraftDefinition:
    title: str
    author: str
    blocks_data: dict

_BLOCKMAP = None

def get_blockmap(use_cache: bool):
    global _BLOCKMAP
    if _BLOCKMAP is None:
        cache_file = Path(os.getcwd()).joinpath('', 'blockmap.csv')
        if not cache_file.exists() or not use_cache:
            response = requests.get('https://raw.githubusercontent.com/gbl/GrabcraftLitematic/master/blockmap.csv')
            if (response.status_code > 299):
                raise Exception(f"Failed to download blockmap: {response.status_code}")
            cache_file.write_text(response.text)
        
        raw_map = cache_file.read_text().split('\n')
        _BLOCKMAP = {}
        for line in raw_map:
            if line == '':
                continue

            line_data = line.split('\t')
            grabcraft = line_data[0] or ''
            minecraft = line_data[1] or ''

            _BLOCKMAP[grabcraft] = minecraft

    return _BLOCKMAP

def download_definition(url: str) -> GrabcraftDefinition:
    response = requests.get(url)
    if response.status_code > 299:
        raise Exception(f"Failed to download definition: {response.status_code}")
    
    html = response.text

    title_regex = re.compile(r'id="content-title"[^>]+>([^<]+)', re.MULTILINE)
    matches = title_regex.search(html)
    if matches is None:
        raise Exception("Failed to find design title")
    title = matches[1].strip()

    author_regex = re.compile(r'Author: ([^<]+)', re.MULTILINE)
    matches = author_regex.search(html.replace('&nbsp;', ' '))
    if matches is None:
        raise Exception("Failed to find design's author")
    author = matches[1].strip()

    blocks_regex = re.compile(r'(https?://[^.]+?\.grabcraft\.com/js/RenderObject/myRenderObject_[^.]+?\.js)', re.MULTILINE)
    matches = blocks_regex.search(html)
    if matches is None:
        raise Exception("Failed to find definition URL")
    
    definition_url = matches.group(1)
    response = requests.get(definition_url)
    if response.status_code > 299:
        raise Exception(f"Failed to download definition: {response.status_code}")
    
    return GrabcraftDefinition(title=title, author=author, blocks_data=json.loads(re.sub('^[^{]+', '', response.text)))

def get_grabcraft_blocks(schema: dict) -> dict[Coordinates, dict]:
    result: dict[Coordinates, dict] = {}

    for level_key in schema.keys():
        level = schema[level_key]
        for block_key in level.keys():
            block = level[block_key]
            for element_key in block.keys():
                element = block[element_key]
                coordinates = Coordinates(x=int(element['x']), y=int(element['y']), z=int(element['z']))
                result[coordinates] = element
    
    return dict(sorted(result.items(), key=lambda tpl: f'{tpl[0].y:3d}{tpl[0].x:3d}{tpl[0].z:3d}'))

def grabcraft_to_minecraft_type(data: dict, use_cache: bool) -> str:
    blockmap = get_blockmap(use_cache)
    return blockmap[data['name']] if data['name'] in blockmap else f'GRABCRAFT:{data["name"]}'

def get_definition(url: str, use_cache: bool):
    grab_def = download_definition(url)
    raw_blocks = get_grabcraft_blocks(grab_def.blocks_data)

    blocks = {}
    for coord, block in raw_blocks.items():
        blocks[coord] = {
            **block,
            'name': grabcraft_to_minecraft_type(block, use_cache),
        }

    return GenericDefinition(title=grab_def.title, author=grab_def.author, blocks=blocks)