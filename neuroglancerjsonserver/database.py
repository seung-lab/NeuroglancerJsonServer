import os
import zlib
import datetime
from google.cloud import datastore

HOME = os.path.expanduser('~')

# Setting environment wide credential path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
           HOME + "/.cloudvolume/secrets/google-secret.json"

class JsonDataBase(object):
    def __init__(self, project_id="neuromancer-seung-import",
                 client=None, credentials=None):
        if client is not None:
            self._client = client
        else:
            self._client = datastore.Client(project=project_id,
                                            credentials=credentials)

    @property
    def client(self):
        return self._client

    @property
    def namespace(self):
        return 'neuroglancerjsondb'

    @property
    def kind(self):
        return "ngl_json"

    def add_json(self, json_data):
        key = self.client.key(self.kind, namespace=self.namespace)
        entity = datastore.Entity(key, exclude_from_indexes=['json'])
        entity['json'] = zlib.compress(json_data)
        entity['access_counter'] = int(1)

        now = datetime.datetime.utcnow()
        entity['date'] = now
        entity["date_last"] = now

        self.client.put(entity)

        return entity.key.id

    def get_json(self, json_id):
        key = self.client.key(self.kind, json_id, namespace=self.namespace)

        entity = self.client.get(key)
        json_data =  zlib.decompress(entity.get("json"))

        if 'access_counter' in entity:
            entity['access_counter'] += int(1)
        else:
            entity['access_counter'] = int(2)

        entity["date_last"] = datetime.datetime.utcnow()

        self.client.put(entity)

        return json_data