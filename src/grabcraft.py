from dataclasses import dataclass
from pathlib import Path
import json
import re
import os

from bs4 import BeautifulSoup
import requests
import yaml

from src.common import Coordinates, GenericDefinition


@dataclass
class Cardinals:
    north: str
    east: str
    south: str
    west: str

    def get(self, cardinal: str) -> str:
        return getattr(self, cardinal) if hasattr(self, cardinal) else cardinal


@dataclass
class GrabcraftDefinition:
    title: str
    author: str
    blocks_data: dict
    cardinals: Cardinals


CARDINALS = {'N': 'north', 'E': 'east', 'S': 'south', 'W': 'west'}

_BLOCKMAP = None


def get_blockmap():
    global _BLOCKMAP

    if _BLOCKMAP is None:
        blockmap_file = Path(os.getcwd()).joinpath('', 'blockmap.yaml')
        data = yaml.load(blockmap_file.read_text(), Loader=yaml.loader.BaseLoader)

        _BLOCKMAP = data['blocks']

    return _BLOCKMAP


def download_definition(url: str) -> GrabcraftDefinition:
    response = requests.get(url)
    if response.status_code > 299:
        raise Exception(f"Failed to download definition: {response.status_code}")

    raw_html = response.text
    html = BeautifulSoup(raw_html, 'html.parser')

    blueprint_cardinals = {
        'north': CARDINALS[html.find('span', {'id': 'south'}).contents[0]],
        'east': CARDINALS[html.find('span', {'id': 'west'}).contents[0]],
        'south': CARDINALS[html.find('span', {'id': 'north'}).contents[0]],
        'west': CARDINALS[html.find('span', {'id': 'east'}).contents[0]],
    }

    title = str(html.find('h1', {'id': 'content-title'}).contents[0])

    author_regex = re.compile(r'Author: ([^<]+)', re.MULTILINE)
    matches = author_regex.search(raw_html.replace('&nbsp;', ' '))
    if matches is None:
        raise Exception("Failed to find design's author")
    author = matches[1].strip()

    blocks_regex = re.compile(r'(https?://[^.]+?\.grabcraft\.com/js/RenderObject/myRenderObject_[^.]+?\.js)', re.MULTILINE)
    matches = blocks_regex.search(raw_html)
    if matches is None:
        raise Exception("Failed to find definition URL")

    definition_url = matches.group(1)
    response = requests.get(definition_url)
    if response.status_code > 299:
        raise Exception(f"Failed to download definition: {response.status_code}")

    return GrabcraftDefinition(
        title=title,
        author=author,
        cardinals=Cardinals(**blueprint_cardinals),
        blocks_data=json.loads(re.sub('^[^{]+', '', response.text)),
    )


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


def grabcraft_blockmap_data(result: dict, cardinals: Cardinals) -> dict:
    blockmap = get_blockmap()

    result = {**blockmap[result['name']]} if result['name'] in blockmap else {'name': f'GRABCRAFT:{result["name"]}'}

    # Facing normalize
    if 'facing' in result:
        result['facing'] = cardinals.get(result['facing'])

    return result


def grabcraft_to_minecraft_orientation(block_name: str) -> dict[str, any]:
    if 'north' in block_name:
        return {'facing': 'east'}
    elif 'south' in block_name:
        return {'facing': 'west'}
    elif 'east' in block_name:
        return {'facing': 'south'}
    elif 'west' in block_name:
        return {'facing': 'north'}

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


def fix_door_facing(coord: Coordinates, block: dict, blocks: dict[Coordinates, dict]):
    name = block['_grabcraft_name'].lower()
    if 'door' in name and 'upper' in name:
        lower_block = blocks.get(Coordinates(x=coord.x, y=coord.y - 1, z=coord.z))
        if lower_block is None:
            return

        lower_block['hinge'] = block['hinge']

        block['facing'] = lower_block.get('facing')
        block['open'] = lower_block.get('open')
        block['half'] = 'upper'


def fix_double_chests(coord: Coordinates, block: dict, blocks: dict[Coordinates, dict]):
    facing = block.get('facing')
    if 'chest' not in block['name'] or facing is None or 'type' in block:
        return

    neighbours = []
    n_neighbour_coords = Coordinates(coord.y, coord.x, coord.z - 1)
    s_neighbour_coords = Coordinates(coord.y, coord.x, coord.z + 1)
    e_neighbour_coords = Coordinates(coord.y, coord.x + 1, coord.z)
    w_neighbour_coords = Coordinates(coord.y, coord.x - 1, coord.z)

    if facing == 'east':
        neighbours = [blocks.get(n_neighbour_coords), blocks.get(s_neighbour_coords)]
    elif facing == 'west':
        neighbours = [blocks.get(s_neighbour_coords), blocks.get(n_neighbour_coords)]
    elif facing == 'north':
        neighbours = [blocks.get(w_neighbour_coords), blocks.get(e_neighbour_coords)]
    elif facing == 'south':
        neighbours = [blocks.get(e_neighbour_coords), blocks.get(w_neighbour_coords)]

    left_neighbour = neighbours[0]
    right_neighbour = neighbours[1]

    if left_neighbour and left_neighbour['_grabcraft_name'] == block['_grabcraft_name']:
        left_neighbour['type'] = 'left'
        block['type'] = 'right'
    elif right_neighbour and right_neighbour['_grabcraft_name'] == block['_grabcraft_name']:
        right_neighbour['type'] = 'right'
        block['type'] = 'left'


def get_definition(url: str):
    grab_def = download_definition(url)
    raw_blocks = get_grabcraft_blocks(grab_def.blocks_data)

    blocks = {}
    for coord, block in raw_blocks.items():
        blocks[coord] = {
            '_grabcraft_name': block['name'],
            **grabcraft_blockmap_data(block, grab_def.cardinals),
        }

    # second run to fix missing data
    for coord, block in blocks.items():
        fix_door_facing(coord, block, blocks)
        fix_double_chests(coord, block, blocks)

    return GenericDefinition(title=grab_def.title, author=grab_def.author, blocks=blocks)
