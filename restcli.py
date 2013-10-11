#!/usr/bin/env python

import sys, os
from argparse import ArgumentParser
import importlib
import re
import json

import requests

class RestCLI(object):
    """
    REST Client
    """
    def __init__(self, config):
        self.config = config

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
        #parser.add_argument('--host', help='Host to connect to',
        #                    default=self.get_env(self.config, 'host_env'))
        #parser.add_argument('--port', help='Port to connect to',
        #                    default=self.get_env(self.config, 'port_env'))
        parser.add_argument('resource', help='HTTP resource after URI prefix')
        # TODO: Add --uri arg that overrides all above args
        methods_parsers = parser.add_subparsers(help='HTTP methods')
        #method_group = parser.add_mutually_exclusive_group(required=True)
        for method in ['get', 'post', 'put', 'delete']:
            #method_group.add_argument('--' + method, action='store_true')
            m_parser = methods_parsers.add_parser(method)
            m_parser.set_defaults(method=method)
        return parser

    def get_resource(self, res):
        for config_re, resource in self.config['resources'].items():
            if re.search(config_re, res):
                return resource

    def generate_uri(self, uriprefix, res):
        # TODO: If uriprefix env is not there, then ???
        return '{uriprefix}{resource}'.format(uriprefix=uriprefix, resource=res)

    def uri_resource(self, uri):
        res_re = '^https?://.+/' + self.config['uriprefix'].lstrip('/') + '(.+)'
        return re.search(res_re, uri).groups(0)[0]

    def update_body_part(self, body, extra):
        # TODO: Handle arrays like "--server.personality[0].path /etc/a.t"
        parts = extra[0].split('.')
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
                body[part] = extra[1]

    def updated_body_parts(self, body, extras):
        for extra in extras:
            self.update_body_part(body, extra)
        return body

    def parse_extra(self, extra):
        parsed = []
        for i in range(0, len(extra), 2):
            name = extra[i][2:]
            parsed.append((name, extra[i + 1]))
        return parsed

    def json(self, d):
        return json.dumps(d, indent=4)

    def execute(self, args):
        args, extra = self.parse_args(args)
        res = self.get_resource(args.resource)
        uri = self.generate_uri(args.uriprefix, args.resource)
        print 'uri', uri
        method_body = res and res.get(args.method)
        if method_body:
            method_body = self.updated_body_parts(method_body, self.parse_extra(extra))
            print 'Request\n', self.json(method_body)
        r = requests.request(args.method, uri, data=json.dumps(method_body))
        content = r.json()
        if content:
            print 'Got response:\n', self.json(content)


def main(args):
    RestCLI(importlib.import_module(args[0]).config).execute(args[1:])
    #print RestCLI(importlib.import_module(args[0]).config).parse_args(args[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
