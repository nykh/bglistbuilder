from typing import List
import os
import os.path as osp
import csv
import sys

import click

from bgg_api import find_descriptions_on_boardgamegeek, Game

def read_games(file) -> List[str]:
    return map(str.strip, file.readlines())

def try_to_write_to_output_csv(filepath, contents: List[Game]):
    if not contents:
        click.echo('There is nothing to write!')
        return
    try:
        with open(filepath, 'w', newline='') as outfile:
            cw = csv.writer(outfile)
            cw.writerow(Game._fields)
            cw.writerows(contents)
    except Exception as ex:
        raise ex

@click.command()
@click.argument('game_list', type=click.File('r'))
@click.argument('output', type=click.Path())
def main(game_list, output):
    click.echo('Reading from game list...')
    games = read_games(game_list)
    click.echo('Searching your game on boardgamegeek.com...')
    games_with_description = find_descriptions_on_boardgamegeek(games)
    if osp.exists(output) and \
        not click.confirm(f'The file {output} already exists. Do you want to overwrite it?'):
        sys.exit(0)
    click.echo(f'Writing the result to {output}...')
    try_to_write_to_output_csv(output, games_with_description)
    sys.exit(0)

if __name__ == '__main__':
    main()
