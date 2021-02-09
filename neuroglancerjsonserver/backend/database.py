import os
import zlib
import datetime
from google.cloud import datastore

HOME = os.path.expanduser('~')

# Setting environment wide credential path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
           HOME + "/.cloudvolume/secrets/google-secret.json"


class JsonDataBase(object):
    def __init__(self, table_name, project_id=None,
                 client=None, credentials=None):
        if client is not None:
            self._client = client
        else:
            assert project_id is not None
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
    def project_id(self):
        return self.client.project

    @property
    def kind(self):
        return "ngl_json"

    @property
    def json_column(self):
        return 'v1'

    def add_json(self, json_data, user_id, json_id=None, date=None):
        if json_id is None:
            key = self.client.key(self.kind, namespace=self.namespace)
        else:
            key = self.client.key(self.kind, json_id, namespace=self.namespace)
        
        entity = datastore.Entity(key, exclude_from_indexes=(self.json_column,))

        if len(entity.values()):
            raise Exception(f"[{self.namespace}][{key}] ID already exists: {entity}")

        json_data = str.encode(json_data)

        entity[self.json_column] = zlib.compress(json_data)
        entity['access_counter'] = int(1)
        entity['user_id'] = user_id

        now = datetime.datetime.utcnow()
        if date is None:
            date = now

        entity['date'] = date
        entity["date_last"] = now

        self.client.put(entity)

        return entity.key.id

    def get_json(self, json_id, decompress=True):
        key = self.client.key(self.kind, json_id, namespace=self.namespace)

        entity = self.client.get(key)

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
