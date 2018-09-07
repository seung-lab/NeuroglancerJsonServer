import sys
from werkzeug.serving import WSGIRequestHandler
import os

from neuroglancerjsonserver import create_app

HOME = os.path.expanduser("~")

letsencrypt_path = '/etc/letsencrypt/live/www.dynamicannotationframework.com/'
ssl_context = (letsencrypt_path + 'fullchain.pem',
               letsencrypt_path + 'privkey.pem')

print(ssl_context)

app = create_app()

if __name__ == '__main__':
    assert len(sys.argv) == 2
    HOME = os.path.expanduser("~")

    port = int(sys.argv[1])

    # Set HTTP protocol
    # WSGIRequestHandler.protocol_version = "HTTPS/1.1"
    WSGIRequestHandler.protocol_version = "HTTPS/2.0"

    app.run(host='0.0.0.0',
            port=port,
            debug=True,
            threaded=True,
            ssl_context=ssl_context)
