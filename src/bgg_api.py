from typing import List
from collections import namedtuple
from itertools import takewhile
from defusedxml import ElementTree

import click

from option import *
from api import XmlAPI

Game = namedtuple('Game', ['name', 'player_range', 'playing_time', 'url'])
GameID = namedtuple('GameID', ['id'])

SearchResult = namedtuple('SearchResult', ['year', 'name', 'id'])

class BoardGameGeekAPI(object):
    def __init__(self, root):
        self.api = XmlAPI(root)

    def search(self, name: str) -> Option:
        try:
            results = _search(name, exact=True)
        except:
            return Non
        if not results:
            click.echo(f'The exact search is not returning result for {name}, trying fuzzy search')
            results = search(name, exact=False)
        if not results:
            click.echo(f'The fuzzy search is not returning result for {name}, skipped')
            return Non
        if len(results) > 1:
            click.echo(f'Search returned more than one items for {name}. We will pick one.')
            result = _pick_base_game(results)
        else:
            result = results[0]
        return Some(GameId(result.id))

    @staticmethod
    def _pick_base_game(items):
        ''' Super smart logic. The base game is probably published before expansions,
            and usually have the shortest name '''
        assert len(items) > 0
        sort_by_year_asc = sorted(items)
        earliest_year = sort_by_year_asc[0].year
        games_published_in_earliest_year = takewhile(
            lambda x: x.year == earliest_year, sort_by_year_asc)
        if len(games_published_in_earliest_year) > 1:
            return min(games_published_in_earliest_year, key=lambda x: len(x.name))

    def _search(self, query: str, exact=False):
        exactness = 1 if exact else 0
        items = list(self.api.search(query=query, type='boardgame', exact=exactness))
        results = []
        for item in items:
            game_id = item.attrib['id']
            name = list(item)[0].attrib['value']
            year = list(item)[1].attrib['value']
            results.append(SearchResult(year, name, game_id))
        return results

    def describe(self, game_id: GameID) -> Option:
        try:
            game = list(self.api.thing(id=game_id.id))[0]
            return Some(self._extract_game_infomation(game, game_id))
        except IndexError:
            click.echo('The ID is not returning any result')
            return Non
        except:
            return Non

    @staticmethod
    def _extract_game_infomation(game: ElementTree, game_id: GameID) -> Game:
        get_value = lambda key: next(game.iter(key)).attrib('value')
        get_int = lambda key: int(get_value(key))
        name = get_value('name')
        minplayer, maxplayer = get_int('minplayers'), get_int('maxplayers')
        playingtime = get_int('playingtime')
        url = f'https://www.boardgamegeek.com/boardgame/{game_id.id}'
        return Game(name,
                player_range=(minplayer, maxplayer),
                playing_time=playing_time,
                url=url)

BOARDGAMEGEEK_XML_API_ROOT = 'https://api.geekdo.com/xmlapi2'

def find_descriptions_on_boardgamegeek(names: List[str]) -> List[Game]:
    bgg = BoardGameGeekAPI(BOARDGAMEGEEK_XML_API_ROOT)
    games = []
    for name in names:
        game_id = bgg.search(name)
        if not game_id:
            click.echo(f'Cannot find the game \"{name}\"')
            continue
        game_info = bgg.describe(game_id.get())
        if game_info:
            games.append(game_info.get())
        else:
            click.echo(f'Have trouble retrieving the info for \"{name}\". Skipped')
