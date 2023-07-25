import requests
import logging
from clients.omdb import NBotOMDBClient
from schemes.notion import NBotElement
from typing import Dict, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class NBotIMDBSeasonEpisode:
    Title: str
    Released: str
    Episode: str
    imdbRating: str
    imdbID: str


class NBotIMDBSeason:
    Season: str
    Episodes: List[NBotIMDBSeasonEpisode]

    def __init__(self, season):
        self.Season = season
        self.Episodes = []

    def to_notion(self):
        res = [
            {"heading_2": {
                "is_toggleable": True,
                "rich_text": [{"type": "text", "text": {"content": "Сезон {}".format(self.Season)}}]}}
        ]
        for ep in self.Episodes:
            res.append(
                {"heading_3": {
                    "rich_text": [{"type": "text", "text": {
                        "content": "Серия {} — {} — ".format(ep.Episode, ep.Title)}}]}}
            )
            res.append(
                {"paragraph": {"rich_text": [{"type": "text", "text": {"content": "..."}}]}}
            )
        return res


class NBotIMDBElement(NBotElement):
    Title: str
    Year: str
    Rated: str
    Released: str
    Runtime: str
    Genre: str
    Director: str
    Writer: str
    Actors: str
    # Plot: str
    # Language: str
    Country: str
    Awards: str
    # Poster: str
    # Ratings: List[Dict]
    Metascore: str
    imdbRating: str
    # imdbVotes: str
    # imdbID: str
    Type: str
    # Response: str
    notion_types = dict(
        Year="select",
        Rated="select",
        Released="date",
        Genre="multi_select",
        Director="multi_select",
        Actors="multi_select",
        Writer="multi_select",
        Country="multi_select",
        Type="select",
        imdbRating="number",
        Metascore="number",
        Season="number",
        Episode="number",
    )

    props = {}

    def dict(self):
        released = {"start": self.Released} if self.Released else None
        self.props = {
            "Name": {"title": [{"text": {"content": self.Title}}]},
            "year": {"select": {"name": self.Year}},
            "rated": {"select": {"name": self.Rated}},
            "released": {"date": released},
            "runtime": {"rich_text": [{"text": {"content": self.Runtime}}]},
            "genre": {"multi_select": [{"name": item} for item in self.Genre]},
            "director": {"multi_select": [{"name": item} for item in self.Director]},
            "writer": {"multi_select": [{"name": item} for item in self.Writer]},
            "actors": {"multi_select": [{"name": item} for item in self.Actors]},
            "country": {"multi_select": [{"name": item} for item in self.Country]},
            "awards": {"rich_text": [{"text": {"content": self.Awards}}]},
            "metascore": {"number": self.Metascore},
            "imdbrating": {"number": self.imdbRating},
            "type": {"select": {"name": self.Type}},
        }
        return self.props


class NBotOMDBParser:
    content: Dict

    def __init__(self):
        self.client = NBotOMDBClient()
        self.session = requests.Session()
        self.type_map = {
            'episode': NBotIMDBEpisode,
            'movie': NBotIMDBElement,
            'series': NBotIMDBSeries,
        }
        logger.info("{}".format(self.__dict__))

    @staticmethod
    def get_omdb_id(uri):
        parsed_uri = urlparse(uri)
        try:
            return list(filter(None, parsed_uri.path.split('/'))).pop()
        except IndexError:
            logger.error("Unable to get omdb id from {}".format(uri), exc_info=True)
            return None

    def get(self, link) -> (NBotIMDBElement, None):
        imdb_id = self.get_omdb_id(link)
        if not imdb_id:
            logger.error("No imdb id for link {}".format(link))
            return None
        logger.info("Getting the {}".format(imdb_id))
        res = self.session.get(
            self.client.url,
            params=dict(apikey=self.client.key, i=imdb_id),
            timeout=self.client.timeout
        )
        res.raise_for_status()
        self.content = res.json()
        return self.parse()

    def get_season(self, link, number) -> (NBotIMDBSeason, None):
        imdb_id = self.get_omdb_id(link)
        if not imdb_id:
            logger.error("No imdb id for link {}".format(link))
            return None
        logger.info("Getting the {} season {}".format(imdb_id, number))
        res = self.session.get(
            self.client.url,
            params=dict(apikey=self.client.key, i=imdb_id, season=number),
            timeout=self.client.timeout
        )
        res.raise_for_status()
        result = res.json()
        season = NBotIMDBSeason(result['Season'])
        for episode in result['Episodes']:
            item = NBotIMDBSeasonEpisode()
            for k, v in episode.items():
                if k in item.__annotations__.keys():
                    setattr(item, k, v)
                else:
                    logger.info("Skipping {}".format(k))
            season.Episodes.append(item)
        return season

    def parse(self) -> (NBotIMDBElement, None):
        if not self.content:
            return None
        item = self.type_map[self.content["Type"]]()
        for k, v in self.content.items():
            if k in item.__annotations__.keys():
                setattr(item, k, v)
            else:
                logger.info("Skipping {}".format(k))
        item.parse()
        logger.info("Final item: {}".format(item.__dict__))
        return item


class NBotIMDBSeries(NBotIMDBElement):
    Title: str
    Year: str
    Rated: str
    Released: str
    Runtime: str
    Genre: str
    Director: str
    Writer: str
    Actors: str
    # Plot: str
    # Language: str
    Country: str
    Awards: str
    # Poster: str
    # Ratings: List[Dict]
    Metascore: str
    imdbRating: str
    # imdbVotes: str
    # imdbID: str
    Type: str
    # Response: str
    totalSeasons: str

    def dict(self):
        super(NBotIMDBSeries, self).dict()
        try:
            self.props.update({"totalseasons": {"number": float(self.totalSeasons)}})
        except:
            pass
        return self.props


class NBotIMDBEpisode(NBotIMDBElement):
    Title: str
    Year: str
    Rated: str
    Released: str
    Runtime: str
    Genre: str
    Director: str
    Writer: str
    Actors: str
    # Plot: str
    # Language: str
    Country: str
    Awards: str
    # Poster: str
    # Ratings: List[Dict]
    Metascore: str
    imdbRating: str
    # imdbVotes: str
    # imdbID: str
    Type: str
    # Response: str
    Season: str
    Episode: str

    def dict(self):
        super(NBotIMDBEpisode, self).dict()
        self.props.update({"season": {"number": self.Season}, "episode": {"number": self.Episode}})
        return self.props
