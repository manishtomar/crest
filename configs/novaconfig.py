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
    "name": "novacli",
    "description": "CLI to work on Racksapce Nova",
    "uriprefix": {
        "regex": "/v1.0/\d+/",
        "env": "NOVA_URI_PREFIX"
    },
    "headers": {
        "X-Auth-Token": "AS_AUTH_TOKEN"
    },
    "tempfile": "/tmp/nova_req.json",
    "resources": {
        "servers/?$": {
            "post": server,
            "aliases": {
                "name": "server.name"
            },
            "help": "Servers"
        },
        "os-keypairs/?$": {
            "post": keypair
        }
    }
}

