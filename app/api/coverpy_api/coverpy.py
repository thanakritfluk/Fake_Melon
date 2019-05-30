import requests
from . import exceptions


class Result:
    """ Parse an API result into an object format. """

    def __init__(self, item):
        """ Call the list parser. """
        self.parse(item)

    def parse(self, item):
        """ Parse the given list into self variables. """
        try:
            self.artworkThumb = item['artworkUrl100']
        except KeyError as e:
            # A vital parameter is missing, and magic on our end can't get us out of this error case situation.
            # Therefore, we try to save the user from issues (mostly KeyErrors), and stop them from using the public API.
            # Just return a NoResultsException, because the data is corrupt on the API's end,
            # and the library can't use the results.

            # This gets many edge cases in which the API had issues dealing with.
            raise exceptions.NoResultsException

        # The above should prevent most keyerrors, this one is just guarding. However, if something fails here,
        # I can't do much because the API sometimes skips on things and this is _not vital._
        self.artist = item['artistName']
        self.album = item['collectionName']
        self.url = item['url']

        # Take some measures to detect whether it is a song or album
        if 'kind' in item:
            self.type = item['kind'].lower()
        elif 'wrapperType' in item:
            if item['wrapperType'].lower() == 'track':
                self.type = 'song'
            elif item['wrapperType'].lower() == 'collection':
                self.type = 'album'
        elif 'collectionType' in item:
            self.type = 'album'
        else:
            # Assuming edge case of the API
            self.type = 'unknown'

        if self.type == 'song':
            self.name = item['trackName']
        elif self.type == 'album':
            self.name = item['collectionName']
        else:
            self.name = 'unknown'

    def artwork(self, size=625):
        """ Return the artwork to the thumb URL contained. """
        # Replace size because API doesn't hand links to full res. It only gives 60x60 and 100x100.
        # However, I found a way to circumvent it.
        return self.artworkThumb.replace('100x100bb', "%sx%s" % (size, size))


class CoverPy:
    def __init__(self):
        """ Initialize CoverPy. Set a base_url. """
        self.base_url = "https://itunes.apple.com/search/"

    def _get(self, payload, override=False, entities=False):
        """ Get a payload using the base_url. General purpose GET interface """
        if override:
            data = requests.get("%s%s" % (self.base_url, override))
        else:
            payload['entity'] = "musicArtist,musicTrack,album,mix,song"
            payload['media'] = 'music'
            data = requests.get(self.base_url, params=payload)

        if data.status_code != 200:
            return "NONE"
        else:
            return data

    def _search(self, term, limit=1):
        """ Expose a friendlier internal API for executing searches """
        payload = {
            'term': term,
            'limit': limit
        }

        req = self._get(payload)
        return req

    def get_cover(self, term, limit=1, debug=False):
        """ Get an album cover, return a Result object """
        search = self._search(term, limit)
        try:
            parsed = search.json()
        except:
            return "NONE"
        # if parsed['resultCount'] == 0:
        #     raise exceptions.NoResultsException

        result = parsed['results'][0]
        result['url'] = search.url

        return Result(result)
