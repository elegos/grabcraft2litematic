from dataclasses import dataclass
import json
from pathlib import Path
import re
import os

import requests
import yaml

from common import Coordinates, GenericDefinition

@dataclass
class GrabcraftDefinition:
    title: str
    author: str
    blocks_data: dict

_BLOCKMAP = None

def get_blockmap():
    global _BLOCKMAP

    if _BLOCKMAP is None:
        blockmap_file = Path(os.getcwd()).joinpath('', 'blockmap.yaml')
        data = yaml.load(blockmap_file.read_text(), Loader=yaml.loader.BaseLoader)

        # WIP fixes
        if data['version'] != '5':
            for name, block in data['blocks'].items():
                if 'chest' in name.lower() and 'facing' in block:
                    if block['facing'] == 'north': block['facing'] = 'east'
                    if block['facing'] == 'east': block['facing'] = 'south'
                    if block['facing'] == 'south': block['facing'] = 'west'
                    if block['facing'] == 'west': block['facing'] = 'north'

            data['version'] = 5
            yaml.dump(data, blockmap_file.open('w'), sort_keys=False)

        _BLOCKMAP = data['blocks']

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

def grabcraft_blockmap_data(data: dict) -> str:
    blockmap = get_blockmap()

    return blockmap[data['name']] if data['name'] in blockmap else { 'name': f'GRABCRAFT:{data["name"]}' }

def grabcraft_to_minecraft_orientation(block_name: str) -> dict[str, any]:
    if 'north' in block_name:
        return { 'facing': 'east' }
    elif 'south' in block_name:
        return { 'facing': 'west' }
    elif 'east' in block_name:
        return { 'facing': 'south' }
    elif 'west' in block_name:
        return { 'facing': 'north' }

    return {}

def grabcraft_to_minecraft_stairs(block_name: str) -> dict[str, any]:
    extended_args = {}
    if 'stairs' in block_name:
        if 'upside-down' in block_name:
            extended_args['half'] = 'top'
        else:
            extended_args['half'] = 'bottom'
        
        if 'west' in block_name:
            extended_args['facing'] = 'south'
        elif 'east' in block_name:
            extended_args['facing'] = 'north'
    
    return extended_args

def grabcraft_to_minecraft_slabs(block_name: str) -> dict[str, any]:
    extended_args = {}
    if 'slab' in block_name:
        if 'bottom' in block_name:
            extended_args['type'] = 'bottom'
        elif 'top' in block_name:
            extended_args['type'] = 'name'
        elif 'double' in block_name:
            extended_args['type'] = 'double'
    
    return extended_args

def grabcraft_to_minecraft_trapdoors(block_name: str) -> dict[str, any]:
    extended_args = {}
    if 'trapdoor' in block_name:
        if 'closed' in block_name:
            extended_args['open'] = 'false'
        else:
            extended_args['open'] = 'true'
        
        if 'bottom half' in block_name:
            extended_args['half'] = 'bottom'
        else:
            extended_args['half'] = 'top'
        
        if 'west from block' in block_name:
            extended_args['facing'] = 'south'
        elif 'east from block' in block_name:
            extended_args['facing'] = 'east'
        elif 'north from block' in block_name:
            extended_args['facing'] = 'west'
        elif 'south from block' in block_name:
            extended_args['facing'] = 'north'
    
    return extended_args

def grabcraft_to_minecraft_wallsigns(block_name: str) -> dict[str, any]:
    extended_args = {}
    if 'wall sign' in block_name:
        if 'north' in block_name:
            extended_args['facing'] = 'south'
        elif 'south' in block_name:
            extended_args['facing'] = 'north'
        elif 'east' in block_name:
            extended_args['facing'] = 'west'
        elif 'west' in block_name:
            extended_args['facing'] = 'east'
    
    return extended_args

def grabcraft_to_minecraft_props(block: dict) -> dict[str, any]:
    name = str(block['name']).lower()
    return {
        # **grabcraft_to_minecraft_orientation(name),
        # **grabcraft_to_minecraft_stairs(name),
        # **grabcraft_to_minecraft_slabs(name),
        # **grabcraft_to_minecraft_trapdoors(name),
    }

def fix_door_facing(coord: Coordinates, block: dict, blocks: dict[Coordinates, dict]):
    name = block['_grabcraft_name'].lower()
    if 'door' in name and 'upper' in name:
        lower_block = blocks.get(Coordinates(x=coord.x, y=coord.y - 1, z=coord.z))
        if lower_block is None:
            return
        block['facing'] = lower_block.get('facing')

def get_definition(url: str):
    grab_def = download_definition(url)
    raw_blocks = get_grabcraft_blocks(grab_def.blocks_data)

    blocks = {}
    for coord, block in raw_blocks.items():
        blocks[coord] = {
            '_grabcraft_name': block['name'],
            **grabcraft_blockmap_data(block),
        }
    
    # second run to fix missing data
    for coord, block in blocks.items():
        fix_door_facing(coord, block, blocks)

    return GenericDefinition(title=grab_def.title, author=grab_def.author, blocks=blocks)