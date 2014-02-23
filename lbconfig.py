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
    "name": "lbcli",
    "description": "CLI to work on Racksapce Load Balancer",
    "uriprefix": {
        "regex": "/v1.0/\d+/",
        "env": "LB_URI_PREFIX"
    },
    "headers": {
        "X-Auth-Token": "AS_AUTH_TOKEN",
        "Content-Type": "CONTENT_TYPE"
    },
    "tempfile": "/tmp/lb_req.json",
    "resources": {
        "loadbalancers/?$": {
            "post": lb,
            "aliases": {
                "name": "loadBalancer.name"
            },
            "help": "Load balancers"
        },
        "loadBalancers/[\d\-]+/?$": {
            "post": nodes
        },
        "loadBalancers/[\d\-]+/nodes/?$": {
            "post": nodes,
            "help": "Load balancer's nodes. Format: loadBalancers/<load balancer ID>/nodes"
        },
        "loadBalancers/[\d\-]+/nodes/[\d\-]+/?$": {
            "help": "Load balancer's node. Format: loadBalancers/<load balancer ID>/nodes/<nodeID>"
        },
        "loadBalancers/[\d\-]+/metadata/?$": {
            "post": metadata,
            "help": "Load balancer's metadata. Format: loadBalancers/<load balancer ID>/metadata"
        }
    }
}

