# bglistbuilder

A script to retrieve data from Boardgamegeek.com to fill in a game list

To use

```
pipenv install
pipenv run python src/main.py GAME_LIST OUTPUT.csv
```

where `GAME_LIST` is a list of boardgame names, and `OUTPUT.csv` will contain the detailed information found on boardgamegeek.com.

The program does some job disambiguating games when multiple games with the same name exist, and try to fuzzy search when the name in the list is not an exact match on website. Sometimes there can still be exception to the rule, and the program will still guess wrong sometimes.
