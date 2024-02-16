![Grabcraft 2 Litematic logo](./web/static/img/logo.webp)

This script allows to convert a GrabCraft online blueprint into a .litematic file.
This is done by scraping the GrabCraft's blueprint's page, extracting the information blocks data, converting them in actual block states (parsing the GrabCraft's block's name) and writing them in a litematic file, ready to be used with the [Litematica mod](https://github.com/maruohon/litematica).

## Usage

The most simple way to use the tool is visiting the free web application [official instance](https://grabcraft2litematic.giacomofurlan.name/)!

## Local installation

If you don't want to use the hosted service, you can still use the tool either via command line (g2l_cmd.py), or via web app (srv.py via uvicorn).

### Install the dependencies

Install `pipenv` and run `pipenv install`

### CLI

`pipenv run python g2l_cmd.py`

CLI options:

    --url, -u: GrabCraft model URL (if not specified, it will be prompted)
    --output-file-name, -o: custom output file name (default: {design's name}.litematic)

**Note**: in case the output file already exists, it will be prompted if you want to override it; if not, the application will exit without saving.

### Web app

`pipenv run uvicorn srv:app`

## Known limitations

GrabCraft does not expose other information than the block's name, so facing, states and so on so forth are not (directly) included.

The library attempts to recreate the missing information, and thus the general usage of the tool should be just fine. In case of errors, please open an issue!
