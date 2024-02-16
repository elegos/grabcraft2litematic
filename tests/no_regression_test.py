from collections import namedtuple
from dataclasses import dataclass, field
from src import grabcraft
from src.common import Coordinates


@dataclass
class BlockCheck:
    coordinates: tuple[int, int, int]
    name: str
    facing: str
    half: str = field(default=None)
    type: str = field(default=None)
    open: str = field(default=None)
    hinge: str = field(default=None)


def assert_block_state(bp_url: str, elements: list[BlockCheck]):
    definition = grabcraft.get_definition(bp_url)

    for elem in elements:
        assert definition.blocks[Coordinates(*elem.coordinates)].get('name') == elem.name
        assert definition.blocks[Coordinates(*elem.coordinates)].get('facing') == elem.facing
        assert definition.blocks[Coordinates(*elem.coordinates)].get('half') == elem.half
        assert definition.blocks[Coordinates(*elem.coordinates)].get('type') == elem.type


# Example of ↑ West, → North, ↓ East, ← South blueprint
def test_wnes_large_medieval_town_house_1():
    assert_block_state(
        'https://www.grabcraft.com/minecraft/large-medieval-town-house-1',
        [
            # Trapdoors (all directions, half bottom, open only)
            BlockCheck((8, 2, 5), 'minecraft:oak_trapdoor', 'west', 'bottom'),
            BlockCheck((8, 6, 1), 'minecraft:oak_trapdoor', 'north', 'bottom'),
            BlockCheck((8, 6, 17), 'minecraft:oak_trapdoor', 'south', 'bottom'),
            BlockCheck((8, 18, 5), 'minecraft:oak_trapdoor', 'east', 'bottom'),

            # Ladders (south only)
            BlockCheck((2, 9, 4), 'minecraft:ladder', 'south', None),

            # Stairs (all directions, top / bottom half)
            BlockCheck((2, 4, 5), 'minecraft:stone_brick_stairs', 'east', 'bottom'),
            BlockCheck((2, 6, 15), 'minecraft:stone_brick_stairs', 'north', 'bottom'),
            BlockCheck((2, 12, 3), 'minecraft:stone_brick_stairs', 'south', 'bottom'),
            BlockCheck((2, 16, 5), 'minecraft:stone_brick_stairs', 'west', 'bottom'),
            BlockCheck((4, 7, 3), 'minecraft:stone_brick_stairs', 'south', 'top'),
            BlockCheck((6, 4, 5), 'minecraft:stone_brick_stairs', 'east', 'top'),
            BlockCheck((6, 5, 4), 'minecraft:spruce_stairs', 'north', 'top'),
            BlockCheck((6, 5, 5), 'minecraft:spruce_stairs', 'west', 'top'),
        ]
    )


def test_wnes_fantasy_town_small_house_2():
    assert_block_state(
        'https://www.grabcraft.com/minecraft/fantasy-town-small-house-2/other-193',
        [
            # Wall sign (north only)
            BlockCheck((3, 8, 3), 'minecraft:oak_wall_sign', 'north', None),

            # Chests (single, double, all facings)
            BlockCheck((2, 5, 16), 'minecraft:chest', 'north', None, 'left'),
            BlockCheck((2, 6, 16), 'minecraft:chest', 'north', None, 'right'),
            BlockCheck((2, 8, 3), 'minecraft:chest', 'north', None, None),
            BlockCheck((2, 13, 5), 'minecraft:chest', 'south', None, 'right'),
            BlockCheck((2, 14, 5), 'minecraft:chest', 'south', None, 'left'),
            BlockCheck((2, 15, 14), 'minecraft:chest', 'west', None, 'right'),
            BlockCheck((2, 15, 15), 'minecraft:chest', 'west', None, 'left'),
            BlockCheck((6, 4, 10), 'minecraft:chest', 'east', None, 'left'),
            BlockCheck((6, 4, 11), 'minecraft:chest', 'east', None, 'right'),

            # Hopper (facing north)
            BlockCheck((6, 13, 9), 'minecraft:hopper', 'north', None, None),

            # Doors
            BlockCheck((2, 5, 12), 'minecraft:iron_door', 'east', open='false', hinge='right'),
            BlockCheck((3, 5, 12), 'minecraft:iron_door', 'east', open='false', hinge='right', half='upper'),
            BlockCheck((2, 9, 4), 'minecraft:dark_oak_door', 'north', open='false', hinge='left'),
            BlockCheck((3, 9, 4), 'minecraft:dark_oak_door', 'north', open='false', hinge='left', half='upper'),
            BlockCheck((2, 10, 4), 'minecraft:dark_oak_door', 'north', open='false', hinge='right'),
            BlockCheck((3, 10, 4), 'minecraft:dark_oak_door', 'north', open='false', hinge='right', half='upper'),
            BlockCheck((6, 7, 13), 'minecraft:birch_door', 'west', open='false', hinge='left'),
            BlockCheck((7, 7, 13), 'minecraft:birch_door', 'west', open='false', hinge='left', half='upper'),
        ]
    )


def test_eswn_wild_west_sheriff_house():
    assert_block_state(
        'https://www.grabcraft.com/minecraft/wild-west-sheriffs-house/wooden-houses',
        [
            BlockCheck((4, 7, 3), 'minecraft:oak_wall_sign', 'north'),
        ]
    )
