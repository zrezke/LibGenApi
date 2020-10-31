import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Resource, Api, reqparse
import os

app = Flask(__name__)

api = Api(app)


class Scraper(object):
    def __init__(self, args):
        self.args = args
        self.bs4 = BeautifulSoup()

    def search(self):
        if self.args['search_in'] == "LibGen (Sci-Tech)":
            query = self.args['query']
            if len(query) < 2:
                return {"error":"404 Query must be at least 2 characters."}, 404

            mask = self.args['search_with_mask'] #  0 == Yes; 1 == No
            column = self.args['search_in_fields']
            if column is None:
                column = "def"
            if mask is None:
                mask = "1"
            
            url = f"http://libgen.rs/search.php?req={query}&lg_topic=libgen&open=0&view=simple&res=100&phrase={mask}&column={column}"
            self.source = requests.get(url)
            return query

    #  class of search reult table == "c"
    #  than find tbody
    #  than every td in tbody except first one
    #  than find elements under td i think its mostly <a>
    def scrape(self):
        pass


class SearchLibGen(Resource, Scraper):
    def __init__(self):
        super().__init__(Scraper)

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', required=True)
        parser.add_argument('search_in', required=True)
        parser.add_argument('search_with_mask', required=False)
        parser.add_argument('search_in_fields', required=False)
        self.args = parser.parse_args()
        self.search()
        #  Make method for passing args into crawler

        return {"message": "nig"}, 200

    def post(self):
        return ("404 This API doesn't have post support.", 404)
    
    def delete(self):
        return ("404 This API doesn't have delete support.", 404)



api.add_resource(SearchLibGen, '/searchLibGen')









if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))