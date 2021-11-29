import os
from datetime import datetime
from google.cloud import datastore
from datastoreflex import DatastoreFlex

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
            self._client = DatastoreFlex(project=project_id, credentials=credentials)
        self._namespace = table_name
        self._bucket_name = None

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

    def add_json(self, json_data: dict, user_id: str, json_id: int = None, date=None):
        if json_id is None:
            key = self.client.key(self.kind, namespace=self.namespace)
        else:
            key = self.client.key(self.kind, json_id, namespace=self.namespace)

        try:
            entity = self.client.get(key)
        except:
            entity = None

        assert entity is None, f"[{self.namespace}][{key}][{json_id}] ID already exists."

        entity = datastore.Entity(key, exclude_from_indexes=(self.json_column,))
        entity[self.json_column] = json_data
        entity["access_counter"] = int(1)
        entity["user_id"] = user_id
        now = datetime.utcnow()
        if date is None:
            date = now

        entity["date"] = date
        entity["date_last"] = now
        self.client.put(entity)
        return entity.key.id

    def get_json(self, json_id: int):
        key = self.client.key(self.kind, json_id, namespace=self.namespace)
        entity = self.client.get(key)

        assert self.json_column in entity.keys()
        json_data = entity.get(self.json_column)

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
