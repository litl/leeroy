# Copyright 2012 litl, LLC.  Licensed under the MIT license.

import logging

from flask import Blueprint, current_app, json, request, Response
from werkzeug.exceptions import NotFound

from . import github, jenkins

base = Blueprint("base", __name__)


@base.route("/ping")
def ping():
    return "pong"


def _parse_jenkins_json(request):
    # The Jenkins notification plugin (at least as of 1.4) incorrectly sets
    # its Content-type as application/x-www-form-urlencoded instead of
    # application/json.  As a result, all of the data gets stored as a key
    # in request.form.  Try to detect that and deal with it.
    if len(request.form) == 1:
        try:
            return json.loads(request.form.keys()[0])
        except ValueError:
            # Seems bad that there's only 1 key, but press on
            return request.form
    else:
        return request.form


@base.route("/notification/jenkins", methods=["POST"])
def jenkins_notification():
    data = _parse_jenkins_json(request)

    jenkins_name = data["name"]
    jenkins_number = data["build"]["number"]
    jenkins_url = data["build"]["full_url"]
    phase = data["build"]["phase"]

    logging.debug("Received Jenkins notification for %s %s (%s): %s",
                  jenkins_name, jenkins_number, jenkins_url, phase)

    if phase not in ("STARTED", "COMPLETED"):
        return Response(status=204)

    git_base_repo = data["build"]["parameters"]["GIT_BASE_REPO"]
    git_head_repo = data["build"]["parameters"]["GIT_HEAD_REPO"]
    git_sha1 = data["build"]["parameters"]["GIT_SHA1"]

    repo_config = github.get_repo_config(current_app, git_base_repo)

    if repo_config is None:
        err_msg = "No repo config for {0}".format(git_base_repo)
        logging.warn(err_msg)
        raise NotFound(err_msg)

    desc_prefix = "Jenkins build '{0}' #{1}".format(jenkins_name,
                                                    jenkins_number)

    if phase == "STARTED":
        github_state = "pending"
        github_desc = desc_prefix + " is running"
    else:
        status = data["build"]["status"]

        if status == "SUCCESS":
            github_state = "success"
            github_desc = desc_prefix + " has succeeded"
        elif status == "FAILURE":
            github_state = "failure"
            github_desc = desc_prefix + " has failed"
        elif status == "ABORTED":
            github_state = "error"
            github_desc = desc_prefix + " has encountered an error"

    logging.debug(github_desc)

    github.update_status(current_app,
                         repo_config,
                         git_base_repo,
                         git_sha1,
                         github_state,
                         github_desc,
                         jenkins_url)

    return Response(status=204)


@base.route("/notification/github", methods=["POST"])
def github_notification():
    action = request.json["action"]
    pull_request = request.json["pull_request"]
    number = pull_request["number"]
    html_url = pull_request["html_url"]
    base_repo_name = github.get_repo_name(pull_request, "base")

    logging.debug("Received GitHub pull request notification for "
                  "%s %s (%s): %s",
                  base_repo_name, number, html_url, action)

    if action not in ("opened", "synchronize"):
        return Response(status=204)

    repo_config = github.get_repo_config(current_app, base_repo_name)

    if repo_config is None:
        err_msg = "No repo config for {0}".format(base_repo_name)
        logging.warn(err_msg)
        raise NotFound(err_msg)

    head_repo_name, shas = github.get_commits(current_app,
                                              repo_config,
                                              pull_request)
    logging.debug("Trigging builds for %d commits", len(shas))

    html_url = pull_request["html_url"]

    for sha in shas:
        logging.debug("Scheduling build for %s %s", head_repo_name, sha)
        jenkins.schedule_build(current_app,
                               repo_config,
                               head_repo_name,
                               sha,
                               html_url)

    return Response(status=204)
