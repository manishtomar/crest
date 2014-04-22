server = {
            "server": {
                "flavorRef": "performance1-1",
                "name": "webhead",
                "imageRef": "0d589460-f177-4b0f-81c1-8ab8903ac7d8",
                "metadata": {
                    "mani": "manitest"
                }
            }
        }

keypair = {
        "keypair": { "name": "mani-key-pair", "public_key": "xxx" }
        }

config = {
    "name": "nova",
    "description": "Rackspace Cloud servers",
    "uriprefix": {
        "regex": "/v1.0/\d+/",
        "env": "NOVA_URI_PREFIX"
    },
    "headers": {
        "X-Auth-Token": {"env": "RS_AUTH_TOKEN"},
        "content-type": "application/json"
    },
    "resources": {
        "servers/?$": {
            "templates": {"default": server},
            "aliases": {
                "name": "server.name"
            },
            "help": "Servers"
        },
        "os-keypairs/?$": {
            "templates": {"default": keypair}
        }
    }
}
