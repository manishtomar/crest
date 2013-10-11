group = {
    "groupConfiguration": {
        "name": "manitest",
        "cooldown": 5,
        "minEntities": 0,
        "maxEntities": 25,
        "metadata": {
            "firstkey": "this is a string",
            "secondkey": "1"
        }
    },
    "launchConfiguration": {
        "type": "launch_server",
        "args": {
            "server": {
                "flavorRef": "3",
                "name": "webhead",
                "imageRef": "0d589460-f177-4b0f-81c1-8ab8903ac7d8",
                "metadata": {
                    "mani": "manitest"
                },
                "personality" : [
                    {
                        "path" : "/etc/banner.txt",
                        "contents": "VGhpcyBpcyBhIHRlc3Qgb2YgYmFzZTY0IGVuY29kaW5n"
                    },
                ]
            }
        }
    },
    "scalingPolicies": [
        {
            "name": "Delete all servers",
            "desiredCapacity": 0,
            "cooldown": 3,
            "type": "webhook"
        }
    ]
}

policies = [
    {
        "name": "scale up by one server",
        "change": 1,
        "cooldown": 150,
        "type": "webhook"
    },
    {
        "name": "scale down by 5.5 percent",
        "changePercent": -5.5,
        "cooldown": 6,
        "type": "webhook"
    }
]

config = {
    "name": "Rackspace Auto Scale",
    "description": "CLI to work on Racksapce Autoscale",
    "host_env": "AS_HOST",
    "port_env": "AS_PORT",
    "uriprefix": {
        "regex": "/v1.0/\d+/",
        "env": "AS_URI_PREFIX"
    },
    "resources": {
        "groups/?$": {
            "post": group,
            "aliases": {
                "name": "groupConfiguration.name"
            }
        },
        "groups/[\w\-]+/?$": {
            "put": group,
            "aliases": {
                "name": "groupConfiguration.name"
            },
        },
        "groups/[\w\-]+/policies/?$": {
            "post": policies,
            "aliases": {
                "name": "groupConfiguration.name"
            },
        }
    }
}

