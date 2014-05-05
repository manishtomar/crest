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
    "uriprefix": "https://identity.api.rackspacecloud.com/v2.0",
    "headers": {
        "accept": "application/json",
        "content-type": "application/json"
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

