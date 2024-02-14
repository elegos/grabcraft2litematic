from argparse import ArgumentParser
from pathlib import Path
import re
import sys
from common import get_max_size
from litemapy import BlockState, Region

import grabcraft
from litematic import grabcraft2region

args = ArgumentParser()
args.add_argument('--url', '-u', help='GrabCraft model URL', required=False)
args.add_argument('--no-cache', action='store_true', help='Ignore existing blockmap.csv')
args.add_argument('--output-file-name', '-o', help='Output file name (default: {design name}.litematic)')
args = args.parse_args()

gc_url_re = re.compile(r'^https?://[^.]+?\.?grabcraft\.com/')
url = args.url
while not url or gc_url_re.match(url) is None:
    url = input('Enter GrabCraft model URL: ')

definition = grabcraft.get_definition(url, use_cache=not args.no_cache)
design_size = get_max_size(definition.blocks.keys())

print('')
print(f'Design title:\t{definition.title}')
print(f'Design author:\t{definition.author}')
print(f'Design size:\t{design_size}')
print('')

print('Generating schematic...')
region = grabcraft2region(definition)

file_name = args.output_file_name or f'{definition.title}.litematic'
if Path(__file__).parent.joinpath(file_name).exists():
    overwrite = ''
    while overwrite.lower() not in ['y', 'n']:
        overwrite = input(f'File {file_name} already exists. Overwrite? (y/n) ')
    if overwrite.lower() == 'n':
        sys.exit(0)

print('Writing Litematic...')
region \
    .as_schematic(name = definition.title, author=definition.author) \
    .save(args.output_file_name or f'{definition.title}.litematic')
