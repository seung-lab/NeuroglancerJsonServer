import json


def convert_precomputed_to_graphene_v1(json_data):
    j = json.loads(json_data)

    for l in j["layers"].keys():
        if j["layers"][l]["type"] == 'segmentation':
            if j["layers"][l]['source'].startswith("precomputed://gs://neuroglancer/nkem/pinky100_v0/ws/lost_no-random/bbox1_0"):
                j["layers"][l]['source'] = "graphene://https://www.dynamicannotationframework.com/segmentation/1.0/pinky100_sv16"
            else:
                continue

            if 'chunkedGraph' in j["layers"][l]:
                del j["layers"][l]['chunkedGraph']

    return json.dumps(j)