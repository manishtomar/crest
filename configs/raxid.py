tokens_request = {
    "auth": {
        "passwordCredentials":{
            "username":"REPLACE_USERNAME",
            "password":"REPLACE_PASSWORD"
        }
    }
}

config = {
    "name": "raxid",
    "description": "Rackspace Identity Service",
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

