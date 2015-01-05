import urlparse
import libsonic
import logging
import utils

# Logger instance
logger = logging.getLogger(__name__)


class Connection(libsonic.Connection):
    """
    Extend `libsonic.Connection` with new features and fix a few issues.

    - Add library name property.
    - Parse URL for host and port for constructor.
    - Make sure API results are of correct type.
    """

    def __init__(self, name, url, username, password):
        self.name = name

        # Parse SubSonic URL
        parts = urlparse.urlparse(url)
        scheme = parts.scheme or "http"

        # Make sure there is hostname
        if not parts.hostname:
            raise ValueError("Expected hostname for URL: %s" % url)

        # Validate scheme
        if scheme not in ("http", "https"):
            raise ValueError("Unexpected scheme '%s' for URL: %s" % (
                scheme, url))

        # Pick a default port
        host = "%s://%s" % (scheme, parts.hostname)
        port = parts.port or {"http": 80, "https": 443}[scheme]

        # Invoke original constructor
        super(Connection, self).__init__(host, username, password, port=port)

    def getIndexes(self, *args, **kwargs):
        """
        """

        def _artists_iterator(artists):
            for artist in utils.force_list(artists):
                artist["id"] = int(artist["id"])
                yield artist

        def _index_iterator(index):
            for index in utils.force_list(index):
                index["artist"] = _artists_iterator(index.get("artist"))
                yield index

        response = super(Connection, self).getIndexes(*args, **kwargs)
        response["indexes"] = response.get("indexes", {})
        response["indexes"]["index"] = list(_index_iterator(
            response["indexes"].get("index")))

        return response

    def getPlaylists(self, *args, **kwargs):
        """
        """

        def _playlists_iterator(playlists):
            for playlist in utils.force_list(playlists):
                playlist["id"] = int(playlist["id"])
                yield playlist

        response = super(Connection, self).getPlaylists(*args, **kwargs)
        response["playlists"]["playlist"] = list(
            _playlists_iterator(response["playlists"].get("playlist")))

        return response

    def getPlaylist(self, *args, **kwargs):
        """
        """

        def _entries_iterator(entries):
            for entry in utils.force_list(entries):
                entry["id"] = int(entry["id"])
                yield entry

        response = super(Connection, self).getPlaylist(*args, **kwargs)
        response["playlist"]["entry"] = list(
            _entries_iterator(response["playlist"].get("entry")))

        return response

    def getArtist(self, *args, **kwargs):
        """
        """

        def _albums_iterator(albums):
            for album in utils.force_list(albums):
                album["id"] = int(album["id"])
                yield album

        response = super(Connection, self).getArtist(*args, **kwargs)
        response["artist"]["album"] = list(_albums_iterator(
            response["artist"].get("album")))

        return response

    def getMusicDirectory(self, *args, **kwargs):
        """
        """

        def _children_iterator(children):
            for child in utils.force_list(children):
                child["id"] = int(child["id"])

                if "parent" in child:
                    child["parent"] = int(child["parent"])
                if "coverArt" in child:
                    child["coverArt"] = int(child["coverArt"])
                if "artistId" in child:
                    child["artistId"] = int(child["artistId"])
                if "albumId" in child:
                    child["albumId"] = int(child["albumId"])

                yield child

        response = super(Connection, self).getMusicDirectory(*args, **kwargs)
        response["directory"]["child"] = list(_children_iterator(
            response["directory"].get("child")))

        return response
