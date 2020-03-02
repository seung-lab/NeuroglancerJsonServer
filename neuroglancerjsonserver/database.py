import os
import zlib
import datetime
from google.cloud import datastore

from neuroglancerjsonserver import migration

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

    @property
    def json_column(self):
        return 'v2'

    @property
    def json_col_history(self):
        return "json", 'json_graphene_v1', "v2"

    def add_json(self, json_data):
        key = self.client.key(self.kind, namespace=self.namespace)
        entity = datastore.Entity(key,
                                  exclude_from_indexes=self.json_col_history)

        json_data = migration.convert_precomputed_to_graphene_v1(json_data)
        json_data = str.encode(json_data)

        entity[self.json_column] = zlib.compress(json_data)
        entity['access_counter'] = int(1)

        now = datetime.datetime.utcnow()
        entity['date'] = now
        entity["date_last"] = now

        self.client.put(entity)

        return entity.key.id

    def get_json(self, json_id, decompress=True):
        key = self.client.key(self.kind, json_id, namespace=self.namespace)

        entity = self.client.get(key)

        # Handle data migration to newer formats
        if self.json_column in entity.keys():
            json_data = entity.get(self.json_column)
        elif "json_graphene_v1" in entity.keys():
            # Handles migration from first  graphene format (json_graphene_v1)
            # to flywire migrated format
            entity.exclude_from_indexes.add(self.json_column)

            json_data = zlib.decompress(entity.get("json_graphene_v1"))

            json_data = migration.fafbv2_to_public(json_data)
            json_data = str.encode(json_data)
            json_data = zlib.compress(json_data)

            entity[self.json_column] = json_data
        elif "json" in entity.keys():
            # Handles migration from almost precomputed (json) to first
            # graphene format (json_graphene_v1) to flywire migrated format
            entity.exclude_from_indexes.add(self.json_column)

            json_data = zlib.decompress(entity.get("json"))

            json_data = migration.convert_precomputed_to_graphene_v1(json_data)
            json_data = migration.fafbv2_to_public(json_data)
            json_data = str.encode(json_data)
            json_data = zlib.compress(json_data)

            entity[self.json_column] = json_data
        else:
            raise Exception("Unknown column structure. Show this to an admin.")


        if decompress:
            json_data = zlib.decompress(json_data)

        if 'access_counter' in entity:
            entity['access_counter'] += int(1)
        else:
            entity['access_counter'] = int(2)

        entity["date_last"] = datetime.datetime.utcnow()

        self.client.put(entity)

        return json_data
