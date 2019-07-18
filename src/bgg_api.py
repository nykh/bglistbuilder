from typing import List
from collections import namedtuple
from itertools import takewhile
from defusedxml import ElementTree
import time
from random import random

import click

from option import *
from api import XmlAPI

Game = namedtuple('Game', ['name', 'player_range', 'playing_time', 'url'])
GameId = namedtuple('GameId', ['id'])

SearchResult = namedtuple('SearchResult', ['year', 'name', 'id'])

class Accessor(object):
    def __init__(self, root):
        self.root = root

    def get_value(self, key, default=None):
        try:
            return next(self.root.iter(key)).attrib['value']
        except Exception as ex:
            return default

    def get_int(self, key, default=0):
        v = self.get_value(key)
        return 0 if v is None else int(v)

class BoardGameGeekAPI(object):
    def __init__(self, root):
        self.api = XmlAPI(root)

    def search(self, name: str) -> Option:
        try:
            results = self._search(name, exact=True)
        except Exception as ex:
            print(ex)
            return Non
        if not results:
            click.echo(f'The exact search is not returning result for {name}, trying fuzzy search')
            results = self._search(name, exact=False)
        if not results:
            click.echo(f'The fuzzy search is not returning result for {name}, skipped')
            return Non
        if len(results) > 1:
            click.echo(f'Search returned more than one items for {name}. We will pick one.')
            result = self._pick_base_game(name, results)
        else:
            result = results[0]
        return Some(GameId(result.id))

    @staticmethod
    def _pick_base_game(name, items: List[SearchResult]):
        ''' Super smart logic. The base game is probably published before expansions,
            and usually have the shortest name '''
        assert len(items) > 0

        # We can also try to filter down to those that has a prefix of the name but this doesn't always work out
        names_at_least_contain_the_exact_string = list(filter(lambda r: r.name.startswith(name), items))
        if names_at_least_contain_the_exact_string:
            items = names_at_least_contain_the_exact_string

        sort_by_year_asc = sorted(items)
        earliest_year = sort_by_year_asc[0].year
        games_published_in_earliest_year = list(takewhile(
            lambda x: x.year == earliest_year, sort_by_year_asc))
        if len(games_published_in_earliest_year) > 1:
            return min(games_published_in_earliest_year, key=lambda x: len(x.name))
        else:
            return games_published_in_earliest_year[0]

    def _search(self, query: str, exact=False) -> List[SearchResult]:
        exactness = 1 if exact else 0
        items = list(self.api.search(query=query, type='boardgame', exact=exactness))
        results = []
        for item in items:
            a = Accessor(item)
            game_id = item.attrib['id']
            name = a.get_value('name')
            year = a.get_int('yearpublished', default=float('inf'))
            results.append(SearchResult(year, name, game_id))
        return results

    def describe(self, game_id: GameId) -> Option:
        try:
            game = list(self.api.thing(id=game_id.id))[0]
            return Some(self._extract_game_infomation(game, game_id))
        except IndexError:
            click.echo('The ID is not returning any result')
            return Non
        except Exception as ex:
            print(ex)
            return Non

    @staticmethod
    def _extract_game_infomation(game: ElementTree, game_id: GameId) -> Game:
        a = Accessor(game)
        name = a.get_value('name')
        minplayer, maxplayer = a.get_int('minplayers'), a.get_int('maxplayers')
        playingtime = a.get_int('playingtime')
        url = f'https://www.boardgamegeek.com/boardgame/{game_id.id}'
        return Game(name,
                player_range=f"{minplayer} to {maxplayer}",
                playing_time=playingtime,
                url=url)

BOARDGAMEGEEK_XML_API_ROOT = 'https://api.geekdo.com/xmlapi2'

def sleep_for_random_second(min=0.2, max=1.5):
    random_seconds = min + random() * (max - min)  # 1 to 3
    time.sleep(random_seconds)

def find_descriptions_on_boardgamegeek(names: List[str]) -> List[Game]:
    bgg = BoardGameGeekAPI(BOARDGAMEGEEK_XML_API_ROOT)
    games = []
    for name in names:
        game_id = bgg.search(name)
        sleep_for_random_second()
        if not game_id:
            click.echo(f'Cannot find the game \"{name}\"')
            continue
        game_info = bgg.describe(game_id.get())
        sleep_for_random_second()
        if game_info:
            games.append(game_info.get())
        else:
            click.echo(f'Have trouble retrieving the info for \"{name}\". Skipped')
    return games
