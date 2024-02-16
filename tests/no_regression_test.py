from collections import namedtuple
from src import grabcraft
from src.common import Coordinates

BlockCheck = namedtuple('BlockCheck', ['coordinates', 'name', 'facing', 'half'])


def assert_block_state(bp_url: str, elements: list[BlockCheck]):
    definition = grabcraft.get_definition(bp_url)

    for elem in elements:
        assert definition.blocks[Coordinates(*elem.coordinates)].get('name') == elem.name
        assert definition.blocks[Coordinates(*elem.coordinates)].get('facing') == elem.facing
        assert definition.blocks[Coordinates(*elem.coordinates)].get('half') == elem.half


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
