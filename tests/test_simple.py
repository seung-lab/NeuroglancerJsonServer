import re

def test_simple_json(client):

    url = '/nglstate/post'
    response = client.post(url, json={'key':'value'})
    assert(response.status_code == 200)
    response_re = re.search('.*\/(\d+)', str(response.data))
    response_id = int(response_re.groups()[0])
    assert(response_id>0)
