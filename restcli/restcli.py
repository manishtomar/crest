#!/usr/bin/env python

from __future__ import print_function

import sys, os
from argparse import ArgumentParser
import importlib
import re
import json
import tempfile
import subprocess
from operator import add
import shutil

import requests
from requests.structures import CaseInsensitiveDict

from history import History, HistoryItem


success_codes = [200, 201, 202, 203, 204]


home = os.path.expanduser('~/.restcli')


def extract_config_from_file(fname):
    g = {}
    execfile(fname, g)
    return g['config']


class Service(object):
    """
    RESTful service installed at ~/.restcli
    """
    def __init__(self, name):
        self.path = os.path.join(home, name)
        self.config = extract_config_from_file(os.path.join(self.path, 'config.py'))
        self.history = History(os.path.join(self.path, 'history'))

    @property
    def headers(self):
        headers = CaseInsensitiveDict()
        for name, env_name in self.config['headers'].items():
            env_value = os.getenv(env_name)
            if env_value:
                headers[name] = env_value
        return headers

    def get_template_body(self, res, name):
        res = self.get_resource(res)
        return res['templates'].get(name)

    def get_resource(self, res):
        for config_re, resource in self.config['resources'].items():
            if re.search(config_re, res, re.IGNORECASE):
                return resource

    def uri_prefix(self):
        return os.getenv(self.config['uriprefix']['env'])


def parse_headers(headers):
    parsed_headers = {}
    for header in headers:
        name, value = header.split(':')
        parsed_headers[name] = value
    return parsed_headers


def execute(args):
    """
    Execute with given args
    """
    # Get service
    service = None
    if args.service:
        try:
            service = Service(args.service)
        except Exception as e:
            raise SystemExit('Error: Service not found - ' + str(e))

    process_service_args(service, args)

    history = service and service.history or History(os.path.join(home, 'generic_history'))

    # Print history if asked
    if args.history:
        for item in history.items(False):
            print(item.printable())
        raise SystemExit()

    # Get absolute URI
    res_arg = getattr(args, 'resource/uri')
    uri, res_arg = get_uri(service, history, args.last, args.uriprefix, res_arg)

    # Use last req info but args take precedence
    last_req = args.last and history[args.last] or HistoryItem(None, None)
    method = args.method or last_req.method or 'get'

    # Setup headers
    headers = service and service.headers or CaseInsensitiveDict()
    if args.headers:
        headers.update(parse_headers(args.headers))

    # Get body
    body = get_body(service, last_req, res_arg, args, method, uri, headers)

    # Any printing
    if args.print_only:
        print(method.upper(), uri, '\n{}'.format(body) if body else '')
        raise SystemExit()
    if args.print_body:
        print(method.upper(), uri, '\n{}'.format(body) if body else '')

    # Store request in history
    history.store_item(method.upper(), res_arg, body)

    # Send request
    r = requests.request(method.lower(), uri, data=body, headers=headers)

    # Display response
    content = r.text
    if r.status_code not in success_codes:
        error = 'Error status: {}'.format(r.status_code)
        if content:
            error += '\n{}'.format(pretty(content))
        raise SystemExit(error)
    if content:
        if args.output:
            content = json.loads(content)
            part, prop = extract_body_part(content, args.output)
            print(pretty(part[prop]))
        else:
            print(pretty(content))
    return 0


def setup_parser():
    """ Setup parser """
    parser = ArgumentParser(
        'restcli', description='CLI to access (currently) JSON-based RESTful service')

    generic = parser.add_argument_group('Generic', 'Options that can work without --service')
    generic.add_argument(
        'resource/uri', nargs='?',
        help=('HTTP resource after URI prefix if used with --service '
              '(Use --resources to list possible resources). Otherwise a HTTP URI'))
    generic.add_argument('-H', '--header', metavar='name:value',
                         help='HTTP header. Can be used multiple times',
                         dest='headers', action='append')
    generic.add_argument('-u', '--user', metavar='user:password',
                         help='HTTP Basic authentication credentials')
    generic.add_argument(
        '-m', '--method', help='HTTP method/verb to apply on the resource. '
                               'Defaults to GET if not given')
    generic.add_argument('--get', action='store_true',
                         help='In case of PUT, GET resource and use it as body')
    generic.add_argument('-d', '--data',
                         help=('Request body, prefix it with @ to consider arg as filename '
                               'whose contents will be used as data. Not necessary when used '
                               'with --service. See --template'))
    generic.add_argument('-e', '--edit', help='Edit request before sending. Uses $EDITOR',
                         action='store_true')
    generic.add_argument('-r', '--replace', action='append',
                        metavar='JSON body part=new value',
                        help='Replace JSON body part with new value. Can be used multiple times')
    generic.add_argument('-o', '--output', metavar='JSON body part',
                        help='Output specific part of JSON response body')
    generic.add_argument('--print-only', help='Only print request going to be sent. Does not send',
                        dest='print_only', action='store_true')
    generic.add_argument('--print', help='Print request before sending',
                        dest='print_body', action='store_true')
    generic.add_argument('--history', action='store_true',
                        help=('List requests sent. '
                              'Use --last to use any earlier sent request body.'
                              'Each service based on --service has its own history'))
    generic.add_argument(
        '-l', '--last',
        help=('Use last Nth request body from history. Defaults to 1 if not given. '
              'Use --history to list earlier sent requests'),
        metavar='N', nargs='?', const=1, default=0, type=int)

    # Service management
    generic.add_argument('--install-service', metavar='Config file path',
                         help=('Install service at ~/.restcli described in config file '
                               'so that this service can be used via --service'))
    generic.add_argument('-s', '--service', dest='service',
                         help=('RESTful service installed at ~/.restcli. '
                               'Use --install-service to install service and '
                               '--list-services to list installed services'))
    generic.add_argument('--list-services', action='store_true',
                         help='List installed services')

    # Service specific options
    service = parser.add_argument_group('Service', 'Options that need --service arg')
    service.add_argument('-t', '--template', const='default', nargs='?',
                         help=('Use existing template as request body for the given resource. '
                               'Uses default template if this option is provided without argument. '
                               'See existing templates via --list-templates'))
    service.add_argument('--list-templates', action='store_true',
                         help='List existing templates for given resource')
    service.add_argument('--uriprefix', help='URI prefix overriding configured one')
    service.add_argument('--resources', help='List possible resources', action='store_true')

    return parser


def expand_resource(service, uriprefix_arg, res_arg):
    uriprefix = uriprefix_arg or service.uri_prefix()
    return uriprefix.rstrip('/') + '/' + res_arg


def get_uri(service, history, last, uriprefix, res_arg):
    if not res_arg:
        if not last:
            raise SystemExit('Error: Required resource/URI not given')
        res_arg = history[last].resource
    if res_arg.startswith('http'):
        return res_arg, res_arg
    else:
        return expand_resource(service, uriprefix, res_arg), res_arg


def process_service_args(service, args):
    service_options = ['template', 'list_templates', 'uriprefix', 'resources']
    if not service and any([getattr(args, attr, None) for attr in service_options]):
        raise SystemExit('Error: Required --service argument not given')
    # Print resources if asked
    if args.resources:
        print(*[r.get('help') for r in service.config['resources'].values()], sep='\n')
        raise SystemExit()
    # List templates if asked
    if args.list_templates:
        print('list templates')
        raise SystemExit()
    # install service
    if args.install_service:
        service_name = extract_config_from_file(args.install_service)['name']
        service_path = os.path.join(home, service_name)
        os.makedirs(os.path.join(service_path, 'history'))
        shutil.copyfile(args.install_service, os.path.join(service_path, 'config.py'))
        raise SystemExit()
    # list services
    if args.list_services:
        for _dir in os.listdir(home):
            if _dir == 'generic_history':
                continue
            serv = extract_config_from_file(os.path.join(home, _dir, 'config.py'))
            print('{:<15}{}'.format(serv['name'], serv['description']))
        raise SystemExit()


def get_body(service, last_req, res_arg, args, method, uri, headers):
    """
    Get body of request to be sent
    """
    # TODO: Should it take args as param?

    body = None
    # First try args.data
    if args.data:
        body = open(args.data[1:]).read() if args.data.startswith('@') else args.data
    # Then try template
    elif args.template:
        body = service.get_template_body(res_arg, args.template)
    # then try GET resource for PUT
    elif args.get and method.upper() == 'PUT':
        r = requests.get(uri, headers=headers)
        if r.status_code != 200:
            raise SystemExit('Error: GET {} returned {}. Content:\n{}'.format(
                uri, r.status_code, pretty(r.text)))
        else:
            body = r.json()
    # Then try history
    elif last_req.body:
        body = last_req.body

    # Replace body parts
    if body:
        if args.replace:
            body_replacements = (r.split('=') for r in args.replace)
            body_d = body if isinstance(body, dict) else json.loads(body)
            res = service and service.get_resource(res_arg)
            body = update_body_parts(res, body_d, body_replacements)
        body = body if isinstance(body, basestring) else json.dumps(body, indent=4)
        if args.edit:
            tmpfile = os.path.join(service and service.path or home, '.tmpbody')
            body = get_from_file(tmpfile, body)
    return body


def parse_body_part(name):
    parts = re.split('\[(\d+)\]|(\w+)', name)
    for part in parts:
        if part and part != '.':
            try:
                yield int(part)
            except ValueError:
                yield part


def extract_body_part(body, name):
    for part in parse_body_part(name):
        prev = body
        body = body[part]
    return prev, part


def update_body_part(body, name, new_value):
    part, prop = extract_body_part(body, name)
    try:
        new_value = int(new_value)
    except ValueError:
        pass
    part[prop] = new_value


def update_body_parts(res, body, extras):
    for name, value in extras:
        aliases = res and res.get('aliases')
        if aliases:
            name = aliases.get(name, name)
        update_body_part(body, name, value)
    return body


def get_from_file(fname, content):
    """
    TODO: Need better name?!?
    Display `content` in $EDITOR and return updated content
    """
    editor = os.getenv('EDITOR', 'vim')
    tmpfile = open(fname, 'w')
    with tmpfile:
        tmpfile.write(content)
        tmpfile.flush()
    subprocess.check_call([editor, fname])
    tmpfile = open(fname, 'r')
    with tmpfile:
        return tmpfile.read()


def pretty(s):
    try:
        if isinstance(s, basestring):
            s = json.loads(s)
        return json.dumps(s, indent=4)
    except ValueError:
        return s


def main(args):
    p = setup_parser()
    execute(p.parse_args(args))


if __name__ == '__main__':
    main(sys.argv[1:])
