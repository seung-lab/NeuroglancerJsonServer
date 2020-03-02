import json


def convert_layer_precomputed_to_graphene_v1(layer_obj):
    if layer_obj["type"] == 'segmentation':
        if layer_obj['source'].startswith("precomputed://gs://neuroglancer/nkem/pinky100_v0/ws/lost_no-random/bbox1_0"):
            layer_obj['source'] = "graphene://https://www.dynamicannotationframework.com/segmentation/1.0/pinky100_sv16"
            if 'chunkedGraph' in layer_obj:
                del layer_obj['chunkedGraph']


def convert_precomputed_to_graphene_v1(json_data):
    j = json.loads(json_data)
    layers = j["layers"]

    if isinstance(layers, list):
        for layer in layers:
            convert_layer_precomputed_to_graphene_v1(layer)
    else:
        for l in layers.keys():
            convert_layer_precomputed_to_graphene_v1(layers[l])

    return json.dumps(j)


def convert_layer_fafbv2_to_public(layer_obj):
    if layer_obj["type"] == 'segmentation_with_graph':
        if "fafbv2" in layer_obj['source']:
            table_id = layer_obj['source'].split('/')[-1]
            layer_obj['source'] = f"graphene://https://prodv1.flywire-daf.com/segmentation/table/{table_id}"

            if 'chunkedGraph' in layer_obj:
                del layer_obj['chunkedGraph']


def fafbv2_to_public(json_data):
    j = json.loads(json_data)
    if "fafbv2" in j["jsonStateServer"]:
        j["jsonStateServer"] = "https://globalv1.flywire-daf.com/nglstate/api/v1/post"

    layers = j["layers"]

    if isinstance(layers, list):
        for layer in layers:
            convert_layer_fafbv2_to_public(layer)
    else:
        for l in layers.keys():
            convert_layer_fafbv2_to_public(layers[l])

    return json.dumps(j)