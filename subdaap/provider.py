from subdaap.models import Server

from daapserver.utils import generate_persistent_id
from daapserver import provider

import logging

# Logger instance
logger = logging.getLogger(__name__)


class Provider(provider.Provider):

    # SubSonic has support for artwork.
    supports_artwork = True

    # Persistent IDs are supported.
    supports_persistent_id = True

    def __init__(self, server_name, db, state, connections, cache_manager):
        """
        """

        super(Provider, self).__init__()

        self.server_name = server_name
        self.db = db
        self.state = state
        self.connections = connections
        self.cache_manager = cache_manager

        self.setup_state()
        self.setup_server()

    def setup_state(self):
        """
        """

        if "persistent_id" not in self.state:
            self.state["persistent_id"] = generate_persistent_id()

    def setup_server(self):
        """
        """

        self.server = Server(db=self.db)

        # Set server name and persistent ID.
        self.server.name = self.server_name
        self.server.persistent_id = self.state["persistent_id"]

    def get_artwork_data(self, session, item):
        """
        """

        cache_item = self.cache_manager.artwork_cache.get(item.id)

        if cache_item.iterator is None:
            remote_fd = self.connections[item.database_id].get_artwork_fd(
                item.remote_id, item.file_suffix)
            self.cache_manager.artwork_cache.download(
                item.id, cache_item, remote_fd)

            return cache_item.iterator(), None, None
        return cache_item.iterator(), None, cache_item.size

    def get_item_data(self, session, item, byte_range=None):
        """
        """

        cache_item = self.cache_manager.item_cache.get(item.id)

        if cache_item.iterator is None:
            remote_fd = self.connections[item.database_id].get_item_fd(
                item.remote_id, item.file_suffix)
            self.cache_manager.item_cache.download(
                item.id, cache_item, remote_fd)

            # When a file is being transcoded, the real size is much smaller
            # than the source file size that is stored in the item's metadata.
            # -> return the file size estimated by subsonic from the headers.
            real_file_size = remote_fd.headers.get('content-length',
                                                   item.file_size)
            print("real size: {}".format(real_file_size))

            return cache_item.iterator(byte_range), item.file_type, \
                real_file_size
        return cache_item.iterator(byte_range), item.file_type, \
            cache_item.size
