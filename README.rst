"Curl"REST API Command line client
==================================

A generic CLI to access any RESTful service with a little bit of configuration.
Think of it as something in between curl and proper CLI.

Features:
---------

- Replace parts of JSON request body while sending the request using simple ``object.property[index]`` notation
- Print only part of JSON response using above described notation
- History: Previously sent request are stored and can be resent using ``--last`` option
- Templates: Store preset requests of a particular URL and send them using ``--template`` option
- Service config: Store common headers, URL prefix, preset requests of a particular service in config

It has options similar to curl to fetch and provide request body. ``-d, -H`` and ``-d`` are
same as curl. ``-X`` is changed to ``-m``. Currently, the tool uses ``requests`` to send
HTTP requests. In future, it may just be wrapper on top of curl delegating all options to
curl.

Sample usage:
-------------

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

For more details check `usage <https://github.com/manishtomar/crest/blob/master/usage.md>`_. NOTE: Be careful as this will store request including password in history

Installation
------------
::

   pip install crest
   mkdir -p ~/.crest/generic_history  # for --history and --service to work

Thanks
------

Thanks to Rackspace for having a culture of hacking on side projects and allowing me to work on this, and having an
*excellent* `open source employee contribution policy <https://www.rackspace.com/blog/rackspaces-policy-on-contributing-to-open-source/>`_
