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
    },
    {
        "name": "cron monthly example",
        "change": 1,
        "cooldown": 100,
        "type": "schedule",
        "args": {
            "cron": "* * 3 * *",
        }
    }
]

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
                "flavorRef": "performance1-1",
                "name": "webhead",
                "imageRef": "0d589460-f177-4b0f-81c1-8ab8903ac7d8",
                "metadata": {
                    "mani": "manitest"
                },
                "networks": [
                 {
                     "uuid": "11111111-1111-1111-1111-111111111111"
                 }
                ]
            }
        }
    },
    "scalingPolicies": policies
}

webhooks = [
    {
        "name": "mani-webhook",
        "metadata": {
            "notes": "this is for mani"
        }
    }
]

config = {
    "name": "ascli",
    "description": "Access Rackspace Auto Scale REST API",
    "uriprefix": {
        "regex": "/v1.0/\d+/",
        "env": "AS_URI_PREFIX"
    },
    "headers": {
        "X-Auth-Token": "AS_AUTH_TOKEN"
    },
    "tempfile": "/tmp/ascli_req.json",
    "resources": {
        "groups/?$": {
            "post": group,
            "aliases": {
                "name": "groupConfiguration.name"
            },
            "help": "Scaling groups. Ex: groups"
        },
        "groups/[\w\-]+/?$": {
            "aliases": {
                "name": "groupConfiguration.name"
            },
            "help": "Single scaling group. Format: groups/<groupID> Ex: groups/2339-23-543"
        },
        "groups/[\w\-]+/policies/?$": {
            "post": policies,
            "help": "Scaling group's policies. Format: groups/<groupID>/policies"
        },
        "groups/[\w\-]+/policies/[\w\-]+/?$": {
            "help": "Scaling group's single policy. Format: groups/<groupID>/policies/<policyID>"
        },
        "groups/[\w\-]+/policies/[\w\-]+/webhooks/?$": {
            "post": webhooks,
            "help": "A single policy's webhooks. Format: groups/<groupID>/policies/<policyID>/webhooks"
        }
    }
}

