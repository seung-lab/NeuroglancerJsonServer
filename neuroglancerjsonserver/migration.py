import json


def convert_layer(layer_obj):
    if layer_obj["type"] == 'segmentation' and "source" in layer_obj:
        if layer_obj['source'].startswith("precomputed://gs://neuroglancer/nkem/pinky100_v0/ws/lost_no-random/bbox1_0"):
            layer_obj['source'] = "graphene://https://www.dynamicannotationframework.com/segmentation/1.0/pinky100_sv16"
            if 'chunkedGraph' in layer_obj:
                del layer_obj['chunkedGraph']


def convert_precomputed_to_graphene_v1(json_data):
    j = json.loads(json_data)
    layers = j["layers"]

    if isinstance(layers, list):
        for layer in layers:
            convert_layer(layer)
    else:
        for l in layers.keys():
            convert_layer(layers[l])

    return json.dumps(j)