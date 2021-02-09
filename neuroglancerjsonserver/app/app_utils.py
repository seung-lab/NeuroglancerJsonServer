import os
from flask import current_app
from neuroglancerjsonserver.backend import database
from google.auth import credentials
from google.auth import default as default_creds
from google.cloud import datastore

CACHE = {}


class DoNothingCreds(credentials.Credentials):
    def refresh(self, request):
        pass

def get_datastore_client(config):
    project_id = config.get("PROJECT_ID", None)

    if config.get("emulate", False):
        credentials = DoNothingCreds()
    elif project_id is not None:
        credentials, _ = default_creds()
    else:
        credentials, project_id = default_creds()

    client = datastore.Client(project=project_id,
                              credentials=credentials,
                              namespace=os.environ.get('JSON_DB_TABLE_NAME'))
    return client


def get_json_db():
    if "json_db" not in CACHE:
        client = get_datastore_client(current_app.config)
        CACHE["json_db"] = database.JsonDataBase(client=client)

    return CACHE["json_db"]
