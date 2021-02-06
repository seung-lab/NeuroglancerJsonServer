import os
import zstd
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
    def project_id(self):
        return self.client.project

    @property
    def storage_bucket(self):
        #TODO: implement query and store path in datastore table
        return "/test/"

    @property
    def kind(self):
        return "ngl_json"

    @property
    def json_column(self):
        return 'v1'

    def _write_to_gcs(self, data, path):
    
    def _read_from_gcs(self, path):
        return data


    def add_json(self, json_data, user_id, access_counter=None, date=None, 
                 date_last=None, size_limit_mb=20):
        # Create datastore object first -- need to know ID for GCS write
        key = self.client.key(self.kind, namespace=self.namespace)
        entity = datastore.Entity(key,
                                  exclude_from_indexes=(self.json_column,))

        if access_counter is None:
            access_counter = int(1)
        else:
            access_counter =int(access_counter)
        entity['access_counter'] = access_counter
        entity['user_id'] = user_id

        now = datetime.datetime.utcnow()
        if date_last is None:
            date_last = now
        if date is None:
            date = now
        entity['date'] = date
        entity['date_last'] = date_last

        self.client.put(entity)
        json_id = entity.key.id
        
        # Get enttity and for writing the GCS path 
        key = self.client.key(self.kind, json_id, namespace=self.namespace)
        entity = self.client.get(key)

        # Data handling
        #TODO: ensure all migration is taken care of
        json_data = str.encode(json_data)
        json_data_z = zstd.compress(json_data)
        
        size_compressed_mb = len(json_data_z) / 1024**2
        if size_compressed_mb > size_limit_mb:
            raise Expression(f"Json is too large. The compressed json is {size_compressed_mb}MB.")

        path_to_gcs = f"{storage_bucket}/{user_id}/{json_id}.zstd"
        self._write_json_to_gcs(json_data_z, path_to_gcs)
        entity[self.json_column] = path_to_gcs

        self.client.put(entity)
        return json_id

    def get_json(self, json_id, decompress=True):
        key = self.client.key(self.kind, json_id, namespace=self.namespace)
        entity = self.client.get(key)

        # Handle data migration to newer formats
        assert self.json_column in entity.keys()

        json_data = self._read_from_gcs(entity.get(self.json_column))

        if decompress:
            json_data = zstd.decompress(json_data)

        if 'access_counter' in entity:
            entity['access_counter'] += int(1)
        else:
            entity['access_counter'] = int(2)

        entity["date_last"] = datetime.datetime.utcnow()

        self.client.put(entity)

        return json_data
