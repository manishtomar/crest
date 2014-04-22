lb = {
        "loadBalancer": {
            "name": "mani-test-lb",
            "port": 80,
            "protocol": "HTTP",
            "virtualIps": [
                {
                    "type": "PUBLIC"
                    }
                ]
            }
        }

nodes = {
    "nodes": [
        {
            "address": "10.2.2.3",
            "port": 80,
            "condition": "ENABLED",
            "type":"PRIMARY"
        }
    ]
}

metadata = {
        "metadata": [
            {
                "key":"color",
                "value":"red"
                }
            ]
        }


config = {
    "name": "lbaas",
    "description": "Racksapce Load Balancer",
    "uriprefix": {
        "regex": "/v1.0/\d+/",
        "env": "LB_URI_PREFIX"
    },
    "headers": {
        "X-Auth-Token": {"env": "RS_AUTH_TOKEN"},
        "Content-Type": "application/json"
    },
    "tempfile": "/tmp/lb_req.json",
    "resources": {
        "loadbalancers/?$": {
            "templates": {"default": lb},
            "aliases": {
                "name": "loadBalancer.name"
            },
            "help": "Load balancers"
        },
        "loadBalancers/[\d\-]+/?$": {
            "post": nodes
        },
        "loadBalancers/[\d\-]+/nodes/?$": {
            "templates": {"default": nodes},
            "help": "Load balancer's nodes. Format: loadBalancers/<load balancer ID>/nodes"
        },
        "loadBalancers/[\d\-]+/nodes/[\d\-]+/?$": {
            "help": "Load balancer's node. Format: loadBalancers/<load balancer ID>/nodes/<nodeID>"
        },
        "loadBalancers/[\d\-]+/metadata/?$": {
            "templates": {"default": metadata},
            "help": "Load balancer's metadata. Format: loadBalancers/<load balancer ID>/metadata"
        }
    }
}
