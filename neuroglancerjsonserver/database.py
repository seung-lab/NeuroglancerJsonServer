import os
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
        entity = datastore.Entity(key)
        entity['json'] = json_data

        self.client.put(entity)

        return entity.key.id

    def get_json(self, json_id):
        key = self.client.key(self.kind, json_id, namespace=self.namespace)

        entity = self.client.get(key)
        json_data =  entity.get("json")

        return json_data