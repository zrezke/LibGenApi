import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Resource, Api, reqparse
import sys


app = Flask(__name__)

api = Api(app)


class Scraper(object):
    def __init__(self, args):
        self.args = args
        url = ""

    def search(self):
        url = self.args['link']
        url = url.replace(" ", "+")
        url = url.replace('"AND"', "&")
        url = url.replace("[]", "")
        url = "http://libgen.li/" + url
        if url == None:
            if self.args['search_in'] == "LibGen (Sci-Tech)":
                query = self.args['query']
                query = query.replace(" ", "+")
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
        return self.searchScrape()


    #  searchScrape()
    '''
        Returns this:
        {
            "bookId": {
                "author": ["author", "linkToAuthorSearch"],
                "title": "Title",
                "publisher": "Publisher",
                "year": "xxxx",
                "pages": "xxx",
                "language": "Language",
                "size": "500Kb",
                "extension": "rar",
                "mirrors": ["linktoMiror", "linkToMirror" ...]
            },
        }
    '''
    def searchScrape(self):
        soup = BeautifulSoup(self.source.text, 'html.parser')
        table = soup.find_all("tr", recursive=True)
        result = {}
        for tr in table:
            td = tr.find_all("td")
            if len(td) <= 15 and len(td) >= 12:
                return str(td)
                bookId = td[0].text
                result[bookId] = {}
                thisBook = result[bookId]
                author = td[1].find("a")
                link = author["href"]
                author = author.text
                thisBook["author"] = (author, link)
                title = td[2].find(id=bookId)
                thisBook["title"] = title.contents[0]
                thisBook["publisher"] = td[3].text
                thisBook["year"] = td[4].text
                thisBook["pages"] = td[5].text
                thisBook["language"] = td[6].text
                thisBook["size"] = td[7].text
                thisBook["extension"] = td[8].text
                mirrors = []
                for element in td[9:14]:
                    try:
                        a = element.find("a")
                        mirrors.append(a["href"])
                    except TypeError:
                        pass
                thisBook["mirrors"] = mirrors

        return result, 200


        
class SearchLibGen(Resource, Scraper):
    def __init__(self):
        super().__init__(Scraper)

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('type', required=True)
        self.args = parser.parse_args()
        if self.args['type'] == "search":
            parser.add_argument('query', required=True)
            parser.add_argument('search_in', required=True)
            parser.add_argument('search_with_mask', required=False)
            parser.add_argument('search_in_fields', required=False)
            #  When Adding links use "AND" instead of &!!!!!
            parser.add_argument('link', required=False)
            self.args = parser.parse_args()
            return self.search()

    def post(self):
        return ("404 This API doesn't have post support.", 404)
    
    def delete(self):
        return ("404 This API doesn't have delete support.", 404)



api.add_resource(SearchLibGen, '/searchLibGen')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))