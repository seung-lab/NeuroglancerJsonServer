import sys
from werkzeug.serving import WSGIRequestHandler
import os

from neuroglancerjsonserver.app import create_app

app = create_app()

if __name__ == '__main__':
    assert len(sys.argv) == 3
    HOME = os.path.expanduser("~")

    table_id = sys.argv[1]
    port = int(sys.argv[2])

    # Set HTTP protocol
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    # WSGIRequestHandler.protocol_version = "HTTP/2.0"

    app.run(host='0.0.0.0',
            port=port,
            debug=True,
            threaded=True,
            ssl_context=(HOME + '/keys/server.crt',
                         HOME + '/keys/server.key'))
