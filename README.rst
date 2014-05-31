"Curl"REST API Command line client
==================================

A generic CLI to access any RESTful service with a little bit of configuration.
Think of it as something in between curl and proper CLI.

With following `configuration <https://github.com/manishtomar/crest/blob/master/configs/raxid.py>`_ in ``~/.crest/raxid/config.py``::

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

one can authenticate to `Rackspace Identity Service <http://docs.rackspace.com/auth/api/v2.0/auth-client-devguide/content/QuickStart-000.html>`_
and extract token using following command::

   crest -s raxid tokens -m post -t -r username=myuname -r password=mypwd -o access.token.id

For more details check `usage <https://github.com/manishtomar/crest/blob/master/usage.md>`_

Installation
------------
::

   pip install crest

This will create a `.crest` directory in $HOME and store configurations including history there
