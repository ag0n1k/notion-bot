import requests
import logging
from clients.omdb import NBotOMDBClient
from notion.collection import NotionDate
from datetime import datetime
from utils import get_omdb_id
from typing import Dict

logger = logging.getLogger(__name__)


def check_attr(func):
    def wrapper(obj, attr):
        if hasattr(obj, attr):
            return func(obj, attr)
        return
    return wrapper


class NBotIMDBElement:
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
        Metascore="number"
    )

    def parse(self):
        for i in ["Writer", "Actors", "Director", "Genre"]:
            self.parse_attr(i)
        self.parse_date("Released")
        for i in ["imdbRating", "Metascore"]:
            self.parse_number(i)

    @check_attr
    def parse_number(self, attr):
        attribute = self.__getattribute__(attr)
        try:
            self.__setattr__(attr, float(attribute))
        except ValueError:
            logger.warning("Unable to parse {} setting to 0".format(attr))
            self.__setattr__(attr, float(0))

    @check_attr
    def parse_attr(self, attr):
        attribute = self.__getattribute__(attr)
        self.__setattr__(attr, [i.strip() for i in attribute.split(',')])

    @check_attr
    def parse_date(self, attr):
        attribute = self.__getattribute__(attr)
        try:
            self.__setattr__(attr, NotionDate(datetime.strptime(attribute, '%d %b %Y').date()))
        except ValueError:
            logger.error("Unable to parse date: {}".format(attr))


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

    def get(self, link) -> (NBotIMDBElement, None):
        imdb_id = get_omdb_id(link)
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
