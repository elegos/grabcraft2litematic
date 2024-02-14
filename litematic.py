from litemapy import BlockState, Region

from common import Coordinates, GenericDefinition, get_max_size


def grabcraft2region(definition: GenericDefinition) -> Region:
    design_size = get_max_size(definition.blocks.keys())
    region = Region(0, 0, 0, design_size.x, design_size.y, design_size.z)

    for coordinate, info in definition.blocks.items():
        # WIP: improve with BlockState properties
        props = ['facing', 'half', 'type', 'open', 'half']
        extended_props = {}
        for prop in props:
            if prop in info:
                extended_props[prop] = info[prop]
        region.setblock(coordinate.x - 1, coordinate.y - 1, coordinate.z - 1, BlockState(info['name'], **extended_props))
    
    return region