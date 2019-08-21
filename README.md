# NeuroglancerJsonServer
REST API to serve and store Neuroglancer jsons

## Installation

Not needed for programmatic access, only for hosting. 

```
git clone https://github.com/seung-lab/NeuroglancerJsonServer.git
cd NeuroglancerJsonServer
pip install . --upgrade
```

## Hosting

Currently, the server is hosted at https://www.dynamicannotationframework.com (35.185.22.247). Use the IP address if the website cannot be reached.

## Programmatic access
Using the `requests` package one can post jsons

```
import requests
server_post_address = 'https://www.dynamicannotationframework.com/nglstate/post'
json_id = requests.post('{}'.format(server_post_address), data=json)
```

and get them

```
import requests
server_get_address = 'https://www.dynamicannotationframework.com/nglstate'
json = requests.get('{}/{}'.format(server_get_address, json_id))
```


The `requests` package can be installed via

```
pip install requests
```
