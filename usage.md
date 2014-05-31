# Usage:

Following is help output:
```
usage: crest [-h] [-H name:value] [-u user:password] [-m METHOD] [--get]
             [-d DATA] [-e] [-r JSON body part=new value]
             [-o JSON response part] [--print-only] [--print] [--history]
             [-l [N]] [--install-service Config file path] [-s SERVICE]
             [--list-services] [-t [TEMPLATE]] [--list-templates]
             [--uriprefix URIPREFIX] [--resources]
             [resource/uri]
```
For example below is
command to authenticate to [Rackspace identity service](http://docs.rackspace.com/auth/api/v2.0/auth-client-devguide/content/QuickStart-000.html)
```
crest https://identity.api.rackspacecloud.com/v2.0/tokens -m post -H "content-type:application/json" \
     -d '{"auth":{"passwordCredentials":{"username":"theUserName","password":"thePassword"}}}'
```
In above command, `-m` takes HTTP method in case-insensitive form, -H and -d are same as in curl.
Just as in curl, @[full-path-to-file] can also be passed to -d, causing the contents of that
file to be used as the request body. crest pretty-prints the response if it is able to parse the response
as JSON. Otherwise, it prints the raw response.

To change request body, you can use `-r` option that takes "JSON body part=value" as argument.
In above case if you had request body stored in /req/tokens.json you can do
```
crest https://identity.api.rackspacecloud.com/v2.0/tokens -m post -H "content-type:application/json" \
            -d @/reqs/tokens.json
            -r auth.passwordCredentials.username=myusername -r auth.passwordCredentials.password=mypassword \
            -o access.token.id
```
This will take contents of /reqs/tokens.json file and replace "theUsername" with "myusername" and "thePassword" with "mypassword"
before sending request, i.e. `{"auth":{"passwordCredentials":{"username":"myusername","password":"mypassword"}}}`
will be the sent request.
It does this by splitting the "JSON body part" based on '.' and accessing the JSON content.
It is similar to accessing properties of JavaScript object. One can also index arrays in JSON.
So, `a[2][1].b` will extract 5 out of `{"a": [2, 8, ["some", {"b": 5}]]}`.
It is ok to give arrays in the beginning also: `[0].a.b`.

**Exracting response part**: The same technique is used to extract specific part of the response using -o option. If the
[response](http://docs.rackspace.com/auth/api/v2.0/auth-client-devguide/content/Sample_Request_Response-d1e64.html)
is `{"access":{...,"token":{...,"id": "2329893"}}}`, then only `2329893` will be printed.
This works with subset of JSON response also, i.e. `-o access.token` will pretty-print JSON part.

If you want to be sure what request is being sent, you can use`--print-only` option. This will
print the URI and request body but will not send it. To send it while viewing, use `--print`.

Another way (my favorite) to change the request is using `-e` option. This will open request body
in `$EDITOR` for editing before sending it. The contents in the editor are what will be sent as the
request body i.e. all the `-r` options have already been applied.

## History:
Each request sent to absolute URI is stored in `~/.crest/generic_history/` directory. You can
view previously sent request (called history) using `--history` option. It will display in chronological
order with most recent one on top. For example, in following output:
```
1     GET       http://192.168.24.128:9000/health
2     GET       https://identity.api.rackspacecloud.com/v2.0/sdsd
3     GET       http://192.168.24.128:9000/v1.0/825948/groups/123/policies
4     GET       https://api.github.com/repos/rackerlabs/otter/events
```
the last request sent was `GET http://192.168.24.128:9000/health`. The previous was request numbered 2
and so on.
You can resend or use parts of any previous request using `-l` option. It takes the request number
given in history as argument. It can be given without an argument in which case it defaults to 1 (last request).
In above case, giving `crest -l 1 -m post` will send `POST http://192.168.24.128:9000/health`.
It takes the URI from history and applies method given in cmd-line arg. The command-line arguments always
takes precedence over history.

## Service:
crest is most useful when used with `--service` argument. When sending multiple requests to one
particular service there are many common things like initial part of the URL, the request body with
only part of it being different. You can specify many of these items in a config file
(a python file) and install it using `--install-service` option. For example, below is
[config file](https://github.com/manishtomar/crest/blob/master/configs/raxid.py)
for [Rackspace Identity Service](http://docs.rackspace.com/auth/api/v2.0/auth-client-devguide/content/QuickStart-000.html):
```
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
            "help": "Authenticate via username/password"
        }
    }
}
```
The file with above contents need to be installed using `crest --install-service raxid.py`
before using it with `-s raxid` option. For example  giving below command
```
crest -s raxid tokens -m post -t -r username=myuname -r password=mypwd -o access.token.id
```
after installing the service will send `POST https://identity.api.rackspacecloud.com/v2.0/tokens` with
```
{
    "auth": {
        "passwordCredentials":{
            "username":"myuname",
            "password":"mypwd"
        }
    }
}
```
as request body. Note that only tokens was given instead of full URI. The full URI is taken from config's
`uriprefix` option and "tokens" was appended to it. The `-t` option asks the tool to use "default" template
of "tokens" resource as request body. The "tokens" resource's configuration is taken from "resources" by
matching the "tokens/?$" regexp with resource given in the command line. As described earlier `-r`
takes JSON body part=value as argument. Here, "username" in `-r` was replaced by "auth.passwordCredentials.username"
due to "aliases" configuration. The headers given in the config file are sent along with each request.
The `-o` option works as described earlier.

The headers and uriprefix can be taken from environment variable also. To do that, replace the value
with `{"env": "ENV_VAR"}` JSON. So, giving `{"headers": {"X-Auth-Token": {"env": "RS_AUTH_TOKEN"}}}`
in config file will send `X-Auth-Token` header with value taken from `RS_AUTH_TOKEN` environment variable.

There can be many templates to fit different needs. In above case, you can have
```
    ...
    "resources": {
        "tokens/?$": {
            "templates": {
                "default": tokens_request,
                "auth_by_api": {"auth": {"apiCredentials": {"username": "u", "apiKey": "a"}}},
            },
    ...
```
and use `-t auth_by_api` to send [request](http://docs.rackspace.com/auth/api/v2.0/auth-client-devguide/content/POST_authenticate_v2.0_tokens_Token_Calls.html)
that authenticates by API key. However, you will have to use full `auth.apiCredentials.username`
name in `-r` option since it will not find `passwordCredentials` in the request if `-r username=a` is used.

Each service has its own separate history stored in `~/.crest/<service>/history/` that can be viewed by giving `--history` along with `-s` option.
It can be used using `-l` as described earlier.
