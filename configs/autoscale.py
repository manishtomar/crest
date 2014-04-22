policies = [
    {
        "name": "scale up by one server",
        "change": 1,
        "cooldown": 0,
        "type": "webhook"
    },
    {
        "name": "scale up by percentage",
        "changePercentage": 10,
        "cooldown": 0,
        "type": "webhook"
    },
    {
        "name": "scale based on desiredcapacity",
        "desiredCapacity": 10,
        "cooldown": 0,
        "type": "webhook"
    },
    {
        "name": "cron monthly example",
        "change": 1,
        "cooldown": 0,
        "type": "schedule",
        "args": {
            "cron": "* * 3 * *",
        }
    },
    {
        "name": "at example",
        "change": 1,
        "cooldown": 0,
        "type": "schedule",
        "args": {
            "at": "2015-10-15T10:20:00Z"
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
    "name": "autoscale",
    "description": "Rackspace Auto Scale REST API",
    "uriprefix": {
        "regex": "/v1.0/\d+/",
        "env": "AS_URI_PREFIX"
    },
    "headers": {
        "content-type": "application/json",
        "X-Auth-Token": {"env": "RS_AUTH_TOKEN"}
    },
    "resources": {
        "groups/?$": {
            "templates": {"default": group},
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
            "templates": {"default": policies, "webhook_change": [policies[0]],
                          "webhook_change_percent": [policies[1]],
                          "webhook_desired": [policies[2]],
                          "schedule_cron": [policies[3]],
                          "schedule_at": [policies[4]]},
            "help": "Scaling group's policies. Format: groups/<groupID>/policies"
        },
        "groups/[\w\-]+/policies/[\w\-]+/?$": {
            "templates": {"default": policies[0], "webhook_change": policies[0],
                          "webhook_change_percent": policies[1],
                          "webhook_desired": policies[2],
                          "schedule_cron": policies[3],
                          "schedule_at": policies[4]},
            "help": "Scaling group's single policy. Format: groups/<groupID>/policies/<policyID>"
        },
        "groups/[\w\-]+/policies/[\w\-]+/webhooks/?$": {
            "templates": {"default": webhooks},
            "help": "A single policy's webhooks. Format: groups/<groupID>/policies/<policyID>/webhooks"
        }
    }
}

