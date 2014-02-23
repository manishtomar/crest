#!/usr/bin/env python

from __future__ import print_function

import sys, os
from argparse import ArgumentParser
import importlib
import re
import json
import tempfile
import subprocess

import requests


success_codes = [200, 201, 202, 203, 204]

class RestCLI(object):
    """
    REST Client
    """
    def __init__(self, config):
        self.config = config
        self.headers = {}
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
                                   'Defaults to GET if not given', default='get')
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
            metavar='N', nargs='?', const=1, default=1, type=int)
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

    def store_request(self, method, res, body):
        try:
            path = os.path.join(os.path.expanduser('~/.restcli'), self.config['name'], 'history')
            # TODO: Use os.walk instead
            files = os.listdir(path)
            last = int(sorted(files)[-1]) if files else 0
            with open(os.path.join(path, '{:0=5d}'.format(last + 1)), 'w') as f:
                args = body and (method, res, body) or (method, res, )
                print(*args, sep='\n', file=f)
        except IOError:
            pass

    def printable_history(self):
        "Return iterator of printable items in history"
        try:
            path = os.path.join(os.path.expanduser('~/.restcli'), self.config['name'], 'history')
            # TODO: Use os.walk instead
            files = os.listdir(path)
            return (printable_history_item(os.path.join(path, fentry)) for fentry in files)
        except IOError:
            return ''

    def execute(self, args):
        args = self.parse_args(args)
        # Print resources if asked
        if args.resources:
            print(*[r.get('help') for r in self.config['resources'].values()], sep='\n')
            return 0
        # Print history if asked
        if args.history:
            for item in self.printable_history():
                print(item)
            return 0
        # Check resource
        if not args.resource:
            print('Need resource', file=sys.stderr)
            return -1
        res = self.get_resource(args.resource)
        uri = self.generate_uri(args.uriprefix, args.resource)
        if args.headers:
            self._setup_headers(args.headers)
        # Get body
        if args.method.upper() == 'PUT':
            # GET the resource before PUT
            #print 'Getting', uri
            r = requests.get(uri, headers=self.headers)
            if r.status_code != 200:
                print('Error: GET {} returned {}. Content:\n{}'.format(
                    uri, r.status_code, pretty(r.text)))
                return -1
            else:
                body = r.json()
        else:
            body = res and res.get(args.method)
        # Replace body parts
        if body:
            if args.replace:
                body_replacements = (r.split('=') for r in args.replace)
                body = update_body_parts(res, body, body_replacements)
            body = json.dumps(body, indent=4)
            if args.edit:
                body = get_from_file(self.config['tempfile'], body)
        # Store request in history
        self.store_request(args.method.upper(), args.resource, body)
        # Any printing
        if args.print_only:
            print(args.method.upper(), uri, '\n{}'.format(body) if body else '')
            return
        if args.print_body:
            print(args.method.upper(), uri, '\n{}'.format(body) if body else '')
        # Send request
        r = requests.request(args.method.lower(), uri, data=body, headers=self.headers)
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


def printable_history_item(fname):
    try:
        with open(fname) as f:
            lines = f.readlines()
            return '{:<10}{}'.format(lines[0].strip(), lines[1].strip())
    except IOError:
        return ''


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
