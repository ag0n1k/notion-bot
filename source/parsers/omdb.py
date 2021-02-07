import requests
import logging
from utils import MetaSingleton
from typing import Dict, List
logger = logging.getLogger(__name__)


class NBotIMDB(object, metaclass=MetaSingleton):
    url = 'http://www.omdbapi.com'
    content: Dict

    def __init__(self, api_key, timeout=5):
        self.session = requests.Session()
        self.key = api_key
        self.timeout = timeout
        self.type_map = {
            'episode': NBotIMDBEpisode,
            'movie': NBotIMDBMovie,
            'series': NBotIMDBSeries,
        }

    def get(self, imdb_id):
        logger.info("Getting the {}".format(imdb_id))
        res = self.session.get(self.url,
                               params=dict(
                                   apikey=self.key,
                                   i=imdb_id
                               ),
                               timeout=self.timeout)
        res.raise_for_status()
        self.content = res.json()

    def parse(self):
        if not self.content:
            return
        item = self.type_map[self.content["Type"]]()
        item.parse()

    def parse_movie(self):
        pass
    def parse_series(self):
        pass
    def parse_episode(self):
        pass


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
    Ratings: List[Dict[str: str]]
    Metascore: str
    imdbRating: str
    imdbVotes: str
    imdbID: str
    Type: str
    Response: str

    def parse(self):
        for i in ["Writer", "Actors", "Director"]:
            self.parse_attr(i)

    def parse_attr(self, attr):
        attribute = self.__getattribute__(attr)
        self.__setattr__(attr, [i.strip() for i in attribute.split(',')])


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
