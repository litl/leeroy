# Copyright 2012 litl, LLC.  Licensed under the MIT license.

import logging
import logging.config
import os

from flask import Flask

from .base import base
from .github import register_github_hooks


app = Flask("leeroy")

app.config.from_object("leeroy.settings")

if "LEEROY_CONFIG" in os.environ:
    app.config.from_envvar("LEEROY_CONFIG")

logging_conf = app.config.get("LOGGING_CONF")
if logging_conf and os.path.exists(logging_conf):
    logging.config.fileConfig(logging_conf)

logger_name = app.config.get("LOGGER_NAME")
if logger_name:
    logging.root.name = logger_name

app.register_blueprint(base)

if app.config.get("GITHUB_REGISTER_REPO_HOOKS", True):
    register_github_hooks(app)
