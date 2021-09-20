#!/bin/sh

rm -rf .venv build dist &&
        vagrant up ubuntu &&
        vagrant ssh ubuntu --command 'cd /vagrant && $HOME/.local/bin/poetry config virtualenvs.in-project true && $HOME/.local/bin/poetry install && $HOME/.local/bin/poetry run pyinstaller --clean --onefile --add-binary "binaries/linux:." migaku-player-converter.py'
