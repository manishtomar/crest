tokens_request = {
    "auth": {
        "passwordCredentials":{
            "username":"REPLACE_USERNAME",
            "password":"REPLACE_PASSWORD"
        }
    }
}

config = {
    "description": "Rackspace Identity REST API",
    "uriprefix": {
        "regex": "/v2/\d+/",
        "env": "RSID_URI_PREFIX"
    },
    "resources": {
        "tokens/?$": {
            "templates": {"default": tokens_request},
            "aliases": {
                "username": "auth.passwordCredentials.username",
                "password": "auth.passwordCredentials.password",
            },
            "help": "Authenticate with username/password"
        }
    }
}

