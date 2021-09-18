#!/bin/sh

rm -rf .venv build dist &&
        vagrant up &&
        vagrant winrm --command "cd c:\vagrant ; poetry config virtualenvs.in-project true ; poetry install ; poetry run pyinstaller --onefile --clean --add-binary 'binaries;.' migaku-player-converter.py"
