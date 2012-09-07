# Copyright 2012 litl, LLC.  Licensed under the MIT license.

from flask import json, url_for

import logging
import requests

github_base = "https://api.github.com"
github_status_url = github_base + "/repos/{repo_name}/statuses/{sha}"
github_hooks_url = github_base + "/repos/{repo_name}/hooks"
github_commits_url = \
    github_base + "/repos/{repo_name}/pulls/{number}/commits"


def get_repo_name(pull_request, key):
    return pull_request[key]["repo"]["full_name"]


def get_repo_config(app, repo_name):
    for repo_config in app.config["REPOSITORIES"]:
        if repo_name == repo_config["github_repo"]:
            return repo_config


def get_github_auth(app, repo_config):
    user = repo_config.get("github_user",
                           app.config["GITHUB_USER"])
    password = repo_config.get("github_password",
                               app.config["GITHUB_PASSWORD"])

    return user, password


def get_commits(app, repo_config, pull_request):
    head_repo_name = get_repo_name(pull_request, "head")
    build_all_commits = repo_config.get("build_all_commits",
                                        app.config["BUILD_ALL_COMMITS"])
    if build_all_commits:
        number = pull_request["number"]

        base_repo_name = get_repo_name(pull_request, "base")
        url = github_commits_url.format(repo_name=base_repo_name,
                                        number=number)

        response = requests.get(url, auth=get_github_auth(app, repo_config))
        return head_repo_name, [c["sha"] for c in response.json]
    else:
        return head_repo_name, [pull_request["head"]["sha"]]


def update_status(app, repo_config, repo_name, sha, state, desc, target_url):
    url = github_status_url.format(repo_name=repo_name,
                                   sha=sha)
    params = dict(state=state,
                  description=desc,
                  target_url=target_url)
    headers = {"Content-Type": "application/json"}

    logging.debug("Setting status on %s %s to %s", repo_name, sha, state)

    requests.post(url,
                  auth=get_github_auth(app, repo_config),
                  data=json.dumps(params),
                  headers=headers)


def register_github_hooks(app):
    with app.app_context():
        github_endpoint = url_for("base.github_notification", _external=True)

    for repo_config in app.config["REPOSITORIES"]:
        repo_name = repo_config["github_repo"]
        url = github_hooks_url.format(repo_name=repo_name)
        response = requests.get(url, auth=get_github_auth(app, repo_config))

        if not response.ok:
            logging.warn("Unable to install GitHub hook for repo %s: %s %s",
                         repo_name, response.status_code, response.reason)
            continue

        found_hook = False
        for hook in response.json:
            if hook["name"] != "web":
                continue

            if hook['config']['url'] == github_endpoint:
                found_hook = True
                break

        if not found_hook:
            params = {"name": "web",
                      "config": {"url": github_endpoint,
                                 "content_type": "json"},
                       "events": ["pull_request"]}
            headers = {"Content-Type": "application/json"}

            response = requests.post(url,
                                     auth=get_github_auth(app, repo_config),
                                     data=json.dumps(params),
                                     headers=headers)

            if response.ok:
                logging.info("Registered github hook for %s", repo_name)
            else:
                logging.error("Unable to register github hook for %s: %s",
                              repo_name, response.status_code)
