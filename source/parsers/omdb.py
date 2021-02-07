import requests
import logging
from clients.omdb import NBotOMDBClient
from utils import get_omdb_id
from typing import Dict, List

logger = logging.getLogger(__name__)


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
    Plot: str
    Language: str
    Country: str
    Awards: str
    Poster: str
    Ratings: List[Dict]
    Metascore: str
    imdbRating: str
    imdbVotes: str
    imdbID: str
    Type: str
    Response: str
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
    )

    def parse(self):
        for i in ["Writer", "Actors", "Director"]:
            self.parse_attr(i)

    def parse_attr(self, attr):
        attribute = self.__getattribute__(attr)
        self.__setattr__(attr, [i.strip() for i in attribute.split(',')])


class NBotOMDBParser:
    content: Dict

    def __init__(self):
        self.client = NBotOMDBClient()
        self.session = requests.Session()
        self.type_map = {
            'episode': NBotIMDBEpisode,
            'movie': NBotIMDBMovie,
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
        item.__dict__.update(self.content)
        logger.info(item.__dict__)
        item.parse()
        return item


class NBotIMDBMovie(NBotIMDBElement):
    DVD: str
    BoxOffice: str
    Production: str
    Website: str


class NBotIMDBSeries(NBotIMDBElement):
    totalSeasons: str


class NBotIMDBEpisode(NBotIMDBElement):
    Season: str
    Episode: str
    seriesID: str
