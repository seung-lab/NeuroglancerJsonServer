from neuroglancerjsonserver.backend import database

CACHE = {}


def get_json_db():
    if "json_db" not in CACHE:
        CACHE["json_db"] = database.JsonDataBase()

    return CACHE["json_db"]
