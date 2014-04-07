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
    "description": "CLI to work on Racksapce Nova",
    "uriprefix": {
        "regex": "/v1.0/\d+/",
        "env": "NOVA_URI_PREFIX"
    },
    "headers": {
        "X-Auth-Token": "RS_AUTH_TOKEN"
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
