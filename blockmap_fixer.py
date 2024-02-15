import os
from pathlib import Path
import yaml

blockmap_file = Path(os.getcwd()).joinpath('', 'blockmap.yaml')
data = yaml.load(blockmap_file.read_text(), Loader=yaml.loader.BaseLoader)

if int(data['version']) < 20:
    data['version'] = 20
    for name, block in data['blocks'].items():
        if 'bottom half' in name.lower(): block['half'] = 'bottom'
        if 'top half' in name.lower(): block['half'] = 'top'

yaml.dump(data, blockmap_file.open('w'), sort_keys=False)