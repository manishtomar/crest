#!/usr/bin/env python

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
        self._get_env_headers()

    def _get_env_headers(self):
        for header, env_name in self.config['headers'].items():
            env_value = os.getenv(env_name)
            if env_value:
                self.headers[header] = env_value

    def _setup_headers(self, headers):
        pass

    def parse_args(self, args):
        return self.setup_parser().parse_known_args(args)

    def get_env(self, d, env):
        name = d.get(env)
        return name and os.getenv(name)

    def setup_parser(self):
        parser = ArgumentParser(
            self.config['name'], description=self.config['description'])
        parser.add_argument('-H', '--header', help='HTTP header', dest='header')
        # TODO: What to do if uriprefix is not there?
        parser.add_argument('--uriprefix', help='URI prefix',
                            default=self.get_env(self.config['uriprefix'], 'env'))
        parser.add_argument('--resources', help='List possible resources', action='store_true')
        parser.add_argument('-e', '--edit', help='Edit request before sending. Uses $EDITOR',
                            action='store_true')
        parser.add_argument('--sample', help='Print sample request going to be sent',
                            action='store_true')
        parser.add_argument('resource', help='HTTP resource after URI prefix '
                                             '(Use --resources to list possible resources)')
        parser.add_argument(
            'method', nargs='?', help='HTTP method/verb to apply on the resource. '
                                      'Defaults to GET if not given',
            default='GET')
        return parser

    def get_resource(self, res):
        for config_re, resource in self.config['resources'].items():
            if re.search(config_re, res, re.IGNORECASE):
                return resource

    def _setup_aliases(self, res):
        pass

    def generate_uri(self, uriprefix, res):
        # TODO: If uriprefix env is not there, then ???
        prefix = uriprefix.rstrip('/')
        return '{uriprefix}/{resource}'.format(uriprefix=prefix, resource=res)

    def uri_resource(self, uri):
        res_re = '^https?://.+/' + self.config['uriprefix'].lstrip('/') + '(.+)'
        return re.search(res_re, uri).groups(0)[0]

    def update_body_part(self, body, name, new_value):
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
                body[part] = new_value

    def updated_body_parts(self, res, body, extras):
        for name, value in extras:
            aliases = res.get('aliases')
            if aliases:
                name = aliases.get(name, name)
            self.update_body_part(body, name, value)
        return body

    def parse_extra(self, extra):
        parsed = []
        for i in range(0, len(extra), 2):
            name = extra[i][2:]
            parsed.append((name, extra[i + 1]))
        return parsed

    def execute(self, args):
        args, extra = self.parse_args(args)
        self._setup_headers(args.header)
        res = self.get_resource(args.resource)
        uri = self.generate_uri(args.uriprefix, args.resource)
        if args.resources:
            print '\n'.join([r.get('help') for r in self.config['resources'].values()])
            return
        if args.method.upper() == 'PUT':
            # GET the resource before PUT
            print 'Getting', uri
            r = requests.get(uri, headers=self.headers)
            if r.status_code != 200:
                print 'GET returned\n', pretty(r.text)
                return
            else:
                body = r.json()
        else:
            body = res and res.get(args.method)
        if body:
            body = self.updated_body_parts(res, body, self.parse_extra(extra))
            body = json.dumps(body, indent=4)
            if args.edit:
                body = get_from_file(self.config['tempfile'], body)
        if args.sample:
            print 'Sample request\n', body
            return
        print args.method.upper(), uri, '\n{}'.format(body) if body else ''
        r = requests.request(args.method, uri, data=body, headers=self.headers)
        if r.status_code not in success_codes:
            print 'Error status', r.status_code
        content = r.text
        if content:
            print 'Got response:\n', pretty(content)


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
    c.execute(args[1:])
    #print c.parse_args(args[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
