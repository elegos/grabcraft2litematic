# Grabcraft 2 Litematic

This script allows to convert a GrabCraft online blueprint into a .litematic file.
This is done by scraping the GrabCraft's blueprint's page, extracting the information blocks data, converting the type (via blockmap.csv downloaded from the grabcraft2litematic mod's GitHub page) and writing them in a litematic file.

## Known limitations

GrabCraft does not expose other information than the block, so facing, states and so on so forth are not included.

Most of the static blueprints should not have problems, while the most advanced machineries that require precise facing might suffer the most (if hosted on GrabCraft at all).

## Usage

Install the requirements (using pipenv) and either run the g2l_cmd.py command line application, or run srv.py via uvicorn

### pipenv run python g2l_cmd.py

Options:

    --url, -u: GrabCraft model URL (if not specified, it will be prompted)
    --output-file-name, -o: custom output file name (default: {design's name}.litematic)

**Note**: in case the output file already exists, it will be prompted if you want to override it; if not, the application will exit without saving.
