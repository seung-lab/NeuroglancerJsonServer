import os
import zlib
import datetime
from google.cloud import datastore

from neuroglancerjsonserver.backend import migration

HOME = os.path.expanduser('~')

# Setting environment wide credential path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
           HOME + "/.cloudvolume/secrets/google-secret.json"


class JsonDataBase(object):
    def __init__(self, project_id="neuromancer-seung-import",
                 client=None, credentials=None,
                 table_name='neuroglancerjsondb'):
        if client is not None:
            self._client = client
        else:
            self._client = datastore.Client(project=project_id,
                                            credentials=credentials)

        self._namespace = table_name

    @property
    def client(self):
        return self._client

    @property
    def namespace(self):
        return self._namespace

    @property
    def kind(self):
        return "ngl_json"

    @property
    def json_column(self):
        return 'v1'

    def add_json(self, json_data, user_id):
        key = self.client.key(self.kind, namespace=self.namespace)
        entity = datastore.Entity(key,
                                  exclude_from_indexes=(self.json_column,))

        json_data = migration.convert_precomputed_to_graphene_v1(json_data)
        json_data = str.encode(json_data)

        entity[self.json_column] = zlib.compress(json_data)
        entity['access_counter'] = int(1)
        entity['user_id'] = user_id

        now = datetime.datetime.utcnow()
        entity['date'] = now
        entity["date_last"] = now

        self.client.put(entity)

        return entity.key.id

    def get_json(self, json_id, decompress=True):
        key = self.client.key(self.kind, json_id, namespace=self.namespace)

        entity = self.client.get(key)

        # Handle data migration to newer formats
        assert self.json_column in entity.keys()

        json_data = entity.get(self.json_column)

        if decompress:
            json_data = zlib.decompress(json_data)

        if 'access_counter' in entity:
            entity['access_counter'] += int(1)
        else:
            entity['access_counter'] = int(2)

        entity["date_last"] = datetime.datetime.utcnow()

        self.client.put(entity)

        return json_data
