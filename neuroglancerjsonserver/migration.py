import json


def convert_precomputed_to_graphene_v1(json_data):
    j = json.loads(json_data)
    layers = j["layers"]

    def convertLayer(layerObj):
       if layerObj["type"] == 'segmentation':
            if layerObj['source'].startswith("precomputed://gs://neuroglancer/nkem/pinky100_v0/ws/lost_no-random/bbox1_0"):
                layerObj['source'] = "graphene://https://www.dynamicannotationframework.com/segmentation/1.0/pinky100_sv16"
                if 'chunkedGraph' in layerObj:
                    del layerObj['chunkedGraph'] 

    if isinstance(layers, list):
        for layer in layers:
            convertLayer(layer)
    else:
        for l in layers.keys():
            convertLayer(layers[l])

    return json.dumps(j)