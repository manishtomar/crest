REST API Command line client
============================

A generic CLI to access any RESTful service with a little bit of configuration.
Think of it as something in between curl and proper CLI.

Installation:
------------
Since it not yet there in PyPI, you'll have to clone and execute restcli.py. Make sure `requests` is installed in the environment. 

Usage:
-----
There needs to be a config file for each RESTful service you want to access. It is basically a python file with `config` global variable pointing to a dictionary. 
Currently, I've written config file for [Rackspace Auto Scale](http://docs.rackspace.com/cas/api/v1.0/autoscale-gettingstarted/content/Overview.html). 
Please see [asconfig.py](https://github.com/manishtomar/restcli/blob/master/asconfig.py). I'll add other service configs later on.

To use Rackspace Auto Scale service
```
./restcli.py asconfig --help
```
I normally alias above two in a simple variable `ascli`:
```
alias ascli='./restcli.py asconfig'
```
Please note that you'll have to be in restcli/ directory. Next step is to setup two environment variables: 
[AS_URI_PREFIX](https://github.com/manishtomar/restcli/blob/master/asconfig.py#L70) that stores URI prefix of service and 
[AS_AUTH_TOKEN](https://github.com/manishtomar/restcli/blob/master/asconfig.py#L73) that stores the token id after 
authenticating from [Rackspace authentication service](http://docs.rackspace.com/auth/api/v2.0/auth-client-devguide/content/Sample_Request_Response-d1e64.html).
Both of these are defined in config file. 
```
export AS_URI_PREFIX=https://ord.autoscale.api.rackspacecloud.com/v1.0/829456/
export AS_AUTH_TOKEN=3480d9f0df998dd8f9df8d98f9d8f
```
Now, with these set, one can list groups by just typing `ascli groups`. It'll do `GET https://ord.autoscale.api.rackspacecloud.com/v1.0/829456/groups` and print pretty json response. 
To create a group `ascli groups post`. This will send `POST https://ord.autoscale.api.rackspacecloud.com/v1.0/829456/groups` with content taken from config file described in https://github.com/manishtomar/restcli/blob/master/asconfig.py#L78
All these requests are sent with X-Auth-Token:$AS_AUTH_TOKEN header as described in config file. To change the post body before sending, you can give -e option that will open the content in an editor before sending. 
