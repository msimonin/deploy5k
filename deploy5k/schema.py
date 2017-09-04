from jsonschema import validate

KAVLAN="kavlan"
KAVLAN_LOCAL="kavlan-local"
KAVLAN_GLOBAL="kavlan-global"
PROD="prod"
NETWORK_TYPES = [PROD,KAVLAN_GLOBAL, KAVLAN_LOCAL, KAVLAN]

# This is the schema for the abstract description of the resources
SCHEMA = {
    "type": "object",
    "properties": {
        "machines": {"type": "array", "items": {"$ref": "#/machine"}},
        "networks": {"type": "array", "items": {"$ref": "#/network"}, "uniqueItems": True},
    },
    "additionalProperties": False,
    "required": ["machines", "networks"],

    "machine": {
        "title": "Compute",
        "type": "object",
        "properties": {
            "anyOf": [
                {"roles": {"type": "array", "items": {"type": "string"}}},
                {"role": {"type": "string"}}
            ],
            "cluster": {"type": "string"},
            "nodes": {"type": "number"},
            "primary_network": {"type": "string"},
            "secondary_networks": {"type": "array", "items": {"type": "string"}, "uniqueItems": True}
        },
        "required": ["nodes", "cluster"]
    },
    "network": {
        "type": "object",
        "properties": {
            "type": {"enum" : NETWORK_TYPES},
            "role": {"type": "string"},
            "site": {"type": "string"}
        },
        "required": ["type", "site"]
    }
}

def validate_schema(resources):
    return validate(resources, SCHEMA)
