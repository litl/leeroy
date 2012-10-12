#!/usr/bin/env python
# Copyright 2012 litl, LLC.  Licensed under the MIT license.

import sys
from optparse import OptionParser

from leeroy.app import app


def main():
    parser = OptionParser()
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="activate the flask debugger")
    parser.add_option("-u", "--urls",
                      action="store_true", dest="urls", default=False,
                      help="list the url patterns used")
    parser.add_option("-b", "--bind-address",
                      action="store", type="string", dest="host",
                      default="0.0.0.0",
                      help="specify the address on which to listen")
    parser.add_option("-p", "--port",
                      action="store", type="int", dest="port",
                      default=5000,
                      help="specify the port number on which to run")

    (options, args) = parser.parse_args()

    if options.urls:
        from operator import attrgetter
        rules = sorted(app.url_map.iter_rules(), key=attrgetter("rule"))

        # don't show the less important HTTP methods
        skip_methods = set(["HEAD", "OPTIONS"])

        print "URL rules in use:"
        for rule in rules:
            methods = set(rule.methods).difference(skip_methods)

            print "  %s (%s)" % (rule.rule, " ".join(methods))

        sys.exit(0)

    app.debug = options.debug
    app.run(host=options.host, port=options.port)


if __name__ == '__main__':
    main()
