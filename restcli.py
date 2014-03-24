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

import requests


success_codes = [200, 201, 202, 203, 204]

class RestCLI(object):
    """
    REST Client
    """
    def __init__(self, config):
        self.config = config
        self.headers = {}
        self.history = History(os.path.join(os.path.expanduser('~/.restcli'),
                                            self.config['name'], 'history'))
        self._set_env_headers()

    def _set_env_headers(self):
        for header, env_name in self.config['headers'].items():
            env_value = os.getenv(env_name)
            if env_value:
                self.headers[header] = env_value

    def _setup_headers(self, headers):
        for header in headers:
            name, value = header.split(':')
            self.headers[name] = value

    def parse_args(self, args):
        return self.setup_parser().parse_args(args)

    def get_env(self, d, env):
        name = d.get(env)
        return name and os.getenv(name)

    def setup_parser(self):
        parser = ArgumentParser(
            self.config['name'], description=self.config['description'])
        parser.add_argument(
            'resource', nargs='?',
            help='HTTP resource after URI prefix (Use --resources to list possible resources)')
        parser.add_argument('-H', '--header', metavar='Header',
                            help='HTTP header in name:value form. Can be used multiple times',
                            dest='headers', action='append')
        # TODO: What to do if uriprefix is not there?
        parser.add_argument('--uriprefix', help='URI prefix',
                            default=self.get_env(self.config['uriprefix'], 'env'))
        parser.add_argument('--resources', help='List possible resources', action='store_true')
        parser.add_argument('-e', '--edit', help='Edit request before sending. Uses $EDITOR',
                            action='store_true')
        parser.add_argument('--print-only', help='Only print request going to be sent. Does not send',
                            dest='print_only', action='store_true')
        parser.add_argument('--print', help='Print request before sending',
                            dest='print_body', action='store_true')
        parser.add_argument(
            '-m', '--method', help='HTTP method/verb to apply on the resource. '
                                   'Defaults to GET if not given')
        parser.add_argument('-r', '--replace', action='append',
                            metavar='JSON body part=new value',
                            help='Replace JSON body part with new value. Can be used multiple times')
        parser.add_argument('-o', '--output', metavar='JSON body part',
                            help='Output specific part of JSON response body')
        parser.add_argument('--history', action='store_true',
                            help='List requests sent. Use --last to use any earlier sent request body')
        parser.add_argument(
            '-l', '--last',
            help=('Use last Nth request body from history. Defaults to 1 if not given. '
                  'Use --history to list earlier sent requests'),
            metavar='N', nargs='?', const=1, default=0, type=int)
        return parser

    def get_resource(self, res):
        for config_re, resource in self.config['resources'].items():
            if re.search(config_re, res, re.IGNORECASE):
                return resource

    def generate_uri(self, uriprefix, res):
        # TODO: If uriprefix env is not there, then ???
        prefix = uriprefix.rstrip('/')
        return '{uriprefix}/{resource}'.format(uriprefix=prefix, resource=res)

    def uri_resource(self, uri):
        res_re = '^https?://.+/' + self.config['uriprefix'].lstrip('/') + '(.+)'
        return re.search(res_re, uri).groups(0)[0]

    def get_last_info(self, last):
        last_req = last and self.history[last]
        return

    def execute(self, args):
        args = self.parse_args(args)
        # Print resources if asked
        if args.resources:
            print(*[r.get('help') for r in self.config['resources'].values()], sep='\n')
            return
        # Print history if asked
        if args.history:
            for item in self.history.items(False):
                print(item.printable())
            return
        # Check resource
        if not args.last and not args.resource:
            # TODO: Raise exception instead printing and returning -1
            print('Need resource', file=sys.stderr)
            return -1
        # Use last req info but args take precedence
        last_req = args.last and self.history[args.last] or HistoryItem(None, None)
        method = args.method or last_req.method or 'get'
        res_arg = args.resource or last_req.resource
        # TODO: Have option to get body from args
        last_body = last_req.body
        # Get config resource and URI
        res = self.get_resource(res_arg)
        uri = self.generate_uri(args.uriprefix, res_arg)
        if args.headers:
            self._setup_headers(args.headers)
        # Get body
        body = get_body(last_body, method, uri, self.headers, res,
                        args.replace, args.edit, self.config['tempfile'])
        # Any printing
        if args.print_only:
            print(method.upper(), uri, '\n{}'.format(body) if body else '')
            return
        if args.print_body:
            print(method.upper(), uri, '\n{}'.format(body) if body else '')
        # Store request in history
        # TODO: De-dup request - store only if it is different from previous
        self.history.store_item(method.upper(), res_arg, body)
        # Send request
        r = requests.request(method.lower(), uri, data=body, headers=self.headers)
        # Display response
        content = r.text
        if r.status_code not in success_codes:
            print('Error status', r.status_code, '\n', content and pretty(content))
            return -1
        if content:
            if args.output:
                content = json.loads(content)
                part, prop = extract_body_part(content, args.output)
                print(part[prop])
            else:
                print(pretty(content))
        return 0


class History(object):
    """
    History of requests
    """
    def __init__(self, path):
        self.path = path

    def _last(self):
        try:
            with open(os.path.join(self.path, 'HEAD')) as f:
                return int(f.read().strip())
        except IOError:
            return 0

    def _extract_item(self, fpath, index=None, include_body=True):
        with open(fpath) as f:
            lines = f.readlines()
            body = reduce(add, lines[2:], '') if include_body else None
            return HistoryItem(lines[0].strip(), lines[1].strip(), body=body, index=index)

    def items(self, include_body=True):
        try:
            last = self._last()
            for findex in xrange(last, 0, -1):
                yield self._extract_item(os.path.join(self.path, '{:0=5d}'.format(findex)),
                                         index=(last - findex + 1), include_body=include_body)
        except IOError:
            # Stop processing on any error
            pass

    def __getitem__(self, index):
        findex = self._last() + 1 - index
        return self._extract_item(os.path.join(self.path, '{:0=5d}'.format(findex)),
                                  include_body=True)

    def store_item(self, method, resource, body):
        # TODO: Should it take `HistoryItem` as arg?
        new_filename = '{:0=5d}'.format(self._last() + 1)
        with open(os.path.join(self.path, new_filename), 'w') as f:
            args = body and (method, resource, body) or (method, resource, )
            print(*args, sep='\n', file=f)
            with open(os.path.join(self.path, 'HEAD'), 'w') as hf:
                hf.write(new_filename)


class HistoryItem(object):
    # TODO: Since an item is a request not something generic, should the name
    # be changed to Request?

    def __init__(self, method, resource, body=None, index=None):
        self.method = method
        self.resource = resource
        self.body = body
        self.index = index

    def printable(self):
        return '{:<6}{:<10}{}'.format(self.index, self.method, self.resource)


def get_body(last_body, method, uri, headers, res, replace, edit, tmpfile):
    "Get body of request to be sent"
    if last_body:
        body = json.loads(last_body)
    elif method.upper() == 'PUT':
        # GET the resource before PUT
        #print 'Getting', uri
        r = requests.get(uri, headers=headers)
        if r.status_code != 200:
            print('Error: GET {} returned {}. Content:\n{}'.format(
                uri, r.status_code, pretty(r.text)))
            return -1
        else:
            body = r.json()
    else:
        body = res and res.get(method)
    # Replace body parts
    if body:
        if replace:
            body_replacements = (r.split('=') for r in replace)
            body = update_body_parts(res, body, body_replacements)
        body = json.dumps(body, indent=4)
        if edit:
            body = get_from_file(tmpfile, body)
    return body


def update_body_part(body, name, new_value):
    part, prop = extract_body_part(body, name)
    try:
        new_value = int(new_value)
    except ValueError:
        pass
    part[prop] = new_value


def extract_body_part(body, name):
    parts = name.split('.')
    while parts:
        part = parts.pop(0)
        # Check of array
        m = re.match('(.+)\[(\d+)\]$', part)
        if m:
            part = m.groups()[0]
            index = int(m.groups()[1])
        value = body.get(part)
        if isinstance(value, dict) and parts:
            body = value
        elif isinstance(value, list) and parts:
            body = value[index]
        else:
            return body, part


def update_body_parts(res, body, extras):
    for name, value in extras:
        aliases = res.get('aliases')
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
        return json.dumps(json.loads(s), indent=4)
    except ValueError:
        return s


def main(args):
    conf_mod = args[0]
    if conf_mod[-3:] == '.py':
        conf_mod = conf_mod[:-3]
    c = RestCLI(importlib.import_module(conf_mod).config)
    return c.execute(args[1:])
    #print c.parse_args(args[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
