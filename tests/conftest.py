import pytest
from neuroglancerjsonserver import create_app, database
import numpy as np
import tempfile
import shutil
from google.cloud import datastore, exceptions
import subprocess
from neuroglancerjsonserver.database import DoNothingCreds
import grpc
from time import sleep
import os
from signal import SIGTERM
from itertools import product


@pytest.fixture(scope='session')
def settings():
    return 'db_test'


@pytest.fixture(scope='session', autouse=True)
def bigtable_client(request, cg_settings):
    # setup Emulator
    project_id = settings
    emul_host = "localhost:8086"
    os.environ["EMULATOR_HOST"] = emul_host
    datastore_emulator = subprocess.Popen(["gcloud",
                                           "beta",
                                           "emulators",
                                           "datastore",
                                           "start",
                                           "--host-port",
                                           emul_host],
                                          preexec_fn=os.setsid,
                                          stdout=subprocess.PIPE)

    startup_msg = "Waiting for Emulator to start up at {}..."
    print('bteh', startup_msg.format(os.environ["EMULATOR_HOST"]))
    c = datastore.client(project=project_id, credentials=DoNothingCreds())
    retries = 5
    while retries > 0:
        try:
            c.list_instances()
        except exceptions._Rendezvous as e:
            # Good error - means emulator is up!
            if e.code() == grpc.StatusCode.UNIMPLEMENTED:
                print(" Ready!")
                break
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                sleep(1)
            retries -= 1
            print(".")
    if retries == 0:
        print("\nCouldn't start Emulator."
              " Make sure it is setup correctly.")
        exit(1)

    yield c

    # setup Emulator-Finalizer
    def fin():
        try:
            gid = os.getpgid(datastore_emulator.pid)
            os.killpg(gid, SIGTERM)
        except ProcessLookupError:
            pass
        datastore_emulator.wait()
        print('DataStore stopped')
    request.addfinalizer(fin)


@pytest.fixture(scope='session')
def database(request, google_client, settings):
    project_id = settings
    print('creating database {}'.format(project_id))
    db = database.JsonDataBase(project_id=project_id, client=google_client)

    yield db

    def fin():
        # TODO: How to delete?
        # db.table.delete()
        pass
    request.addfinalizer(fin)
    print("\n\nDatabase entries DELETED")

@pytest.fixture(scope='session')
def test_dataset():
    return 'test'


@pytest.fixture(scope='session')
def app(settings):
    project_id = settings

    app = create_app(
        {
            'project_id': project_id,
            'emulate': True,
            'TESTING': True,
            'DATABASE_CONFIG': {
                'emulate': True
            }
        }
    )
    yield app


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()
