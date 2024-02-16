import os
from pathlib import Path
import yaml

blockmap_file = Path(os.getcwd()).joinpath('', 'blockmap.yaml')
data = yaml.load(blockmap_file.read_text(), Loader=yaml.loader.BaseLoader)

if int(data['version']) < 22:
    data['version'] = 22
    for name, block in data['blocks'].items():
        if 'Door (Facing East' in name:
            block['facing'] = 'west'
        if 'Door (Facing West' in name:
            block['facing'] = 'east'
        if 'Door (Facing North' in name:
            block['facing'] = 'south'
        if 'Door (Facing South' in name:
            block['facing'] = 'north'

yaml.dump(data, blockmap_file.open('w'), sort_keys=False)
