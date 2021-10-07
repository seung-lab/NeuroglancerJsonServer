import os
import zlib
from datetime import datetime
from google.cloud import datastore
from cloudfiles import CloudFiles

HOME = os.path.expanduser("~")

# Setting environment wide credential path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    HOME + "/.cloudvolume/secrets/google-secret.json"
)


class JsonDataBase(object):
    def __init__(self, table_name, project_id=None, client=None, credentials=None):
        if client is not None:
            self._client = client
        else:
            assert project_id is not None
            self._client = datastore.Client(project=project_id, credentials=credentials)
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
        return "v1"

    @property
    def bucket_name(self):
        kind = "nsl_json_bucket_name"
        key_name = "gcs_bucket_name"
        key = self.client.key(kind, key_name, namespace=self.namespace)
        entity = self.client.get(key)
        return entity["value"]

    def add_json(self, json_data: dict, user_id: str, json_id: int = None, date=None):
        if json_id is None:
            key = self.client.key(self.kind, namespace=self.namespace)
        else:
            key = self.client.key(self.kind, json_id, namespace=self.namespace)

        try:
            entity = self.client.get(key)
        except:
            entity = None

        if entity is not None:
            raise Exception(f"[{self.namespace}][{key}][{json_id}] ID already exists.")

        entity = datastore.Entity(key, exclude_from_indexes=(self.json_column,))
        data = zlib.compress(json_data)
        self._add_data_to_bucket(str(key.id), user_id, data)
        entity["access_counter"] = int(1)
        entity["user_id"] = user_id
        now = datetime.utcnow()
        if date is None:
            date = now

        entity["date"] = date
        entity["date_last"] = now
        self.client.put(entity)
        return entity.key.id

    def get_json(self, json_id: int, user_id: str, decompress: bool = True):
        key = self.client.key(self.kind, json_id, namespace=self.namespace)
        entity = self.client.get(key)
        json_data = entity.get(self.json_column)
        if json_data is None:
            json_data = self._get_data_from_bucket(str(json_id), user_id)

        if decompress:
            json_data = zlib.decompress(json_data)

        if "access_counter" in entity:
            entity["access_counter"] += int(1)
        else:
            entity["access_counter"] = int(2)

        entity["date_last"] = datetime.utcnow()
        self.client.put(entity)
        return json_data

    def get_user_states_info(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> list:
        from json import loads

        query = self.client.query(kind=self.kind)
        query = query.add_filter("user_id", "=", user_id)
        query = query.add_filter("date", ">=", start_date)
        query = query.add_filter("date", "<=", end_date)
        result = []
        for entity in query.fetch():
            state_info = {}
            state_info["id"] = entity.key
            state_info["user_id"] = entity["user_id"]
            state_info["access_counter"] = entity.get("access_counter")
            state_info["date_created"] = entity["date"]
            state_info["date_accessed"] = entity["date_last"]
            result.append(state_info)
        return result

    def _get_data_from_bucket(self, state_id: str, user_id: str) -> bytes:
        path = f"{self.bucket_name}/{user_id}"
        cf = CloudFiles(path)
        return cf.get(state_id)

    def _add_data_to_bucket(self, state_id: str, user_id: str, data: bytes) -> None:
        path = f"{self.bucket_name}/{user_id}"
        cf = CloudFiles(path)
        cf.put(state_id, data)
