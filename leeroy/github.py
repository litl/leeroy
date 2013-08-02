# Copyright 2012 litl, LLC.  Licensed under the MIT license.

from flask import json, url_for

import logging
import requests
import warnings

github_status_url = "/repos/{repo_name}/statuses/{sha}"
github_hooks_url = "/repos/{repo_name}/hooks"
github_commits_url = "/repos/{repo_name}/pulls/{number}/commits"

# Use requests.Session() objects keyed by github_repo to handle GitHub API
# authentication details (token vs user/pass) and SSL trust options.
request_sessions = {}

BUILD_COMMITS_ALL = "ALL"
BUILD_COMMITS_LAST = "LAST"
BUILD_COMMITS_NEW = "NEW"


def get_api_url(app, repo_config, url):
    base_url = repo_config.get("github_api_base",
            app.config["GITHUB_API_BASE"])

    return base_url + url


def get_repo_name(pull_request, key):
    return pull_request[key]["repo"]["full_name"]


def get_repo_config(app, repo_name):
    for repo_config in app.config["REPOSITORIES"]:
        if repo_name == repo_config["github_repo"]:
            return repo_config


def get_session_for_repo(app, repo_config):
    session = request_sessions.get(repo_config["github_repo"])
    if session is None:
        session = requests.Session()
        session.verify = repo_config.get("github_verify",
            app.config["GITHUB_VERIFY"])

        token = repo_config.get("github_token",
            app.config.get("GITHUB_TOKEN"))

        if token:
            session.headers = {"Authorization": "token " + token}
        else:
            user = repo_config.get("github_user",
                app.config.get("GITHUB_USER"))
            password = repo_config.get("github_password",
                app.config.get("GITHUB_PASSWORD"))
            session.auth = (user, password)
    return session


def get_build_commits(app, repo_config):
    """
    Determine the value for BUILD_COMMITS from the app and repository
    config. Resolves the previous BUILD_ALL_COMMITS = True/False option
    to BUILD_COMMITS = 'ALL'/'LAST' respectively.
    """
    build_commits = repo_config.get("build_commits")
    build_all_commits = repo_config.get("build_all_commits",
                                        app.config.get("BUILD_ALL_COMMITS"))

    if not build_commits and build_all_commits is not None:
        # Determine BUILD_COMMITS from legacy BUILD_ALL_COMMITS
        if build_all_commits:
            build_commits = BUILD_COMMITS_ALL
        else:
            build_commits = BUILD_COMMITS_LAST
        warnings.warn("BUILD_ALL_COMMITS is deprecated. Use the BUILD_COMMITS "
                      "setting instead.", DeprecationWarning)
    elif not build_commits:
        # Determine BUILD_COMMITS from global app config.
        build_commits = app.config["BUILD_COMMITS"]
    return build_commits


def get_commits(app, repo_config, pull_request):
    head_repo_name = get_repo_name(pull_request, "head")
    base_repo_name = get_repo_name(pull_request, "base")
    build_commits = get_build_commits(app, repo_config)

    if build_commits in (BUILD_COMMITS_ALL, BUILD_COMMITS_NEW):
        number = pull_request["number"]

        url = get_api_url(app, repo_config, github_commits_url).format(
            repo_name=base_repo_name,
            number=number)

        s = get_session_for_repo(app, repo_config)
        response = s.get(url)

        commits = [c["sha"] for c in response.json]

        if build_commits == BUILD_COMMITS_NEW:
            commits = [sha for sha in commits if not
                has_status(app, repo_config, base_repo_name, sha)]

        return head_repo_name, commits
    elif build_commits == BUILD_COMMITS_LAST:
        return head_repo_name, [pull_request["head"]["sha"]]
    else:
        logging.error("Invalid value '%s' for BUILD_COMMITS for repo: %s",
                      build_commits, base_repo_name)


def update_status(app, repo_config, repo_name, sha, state, desc,
                  target_url=None):
    url = get_api_url(app, repo_config, github_status_url).format(
        repo_name=repo_name,
        sha=sha)

    params = dict(state=state,
                  description=desc)

    if target_url:
        params["target_url"] = target_url

    headers = {"Content-Type": "application/json"}

    logging.debug("Setting status on %s %s to %s", repo_name, sha, state)

    s = get_session_for_repo(app, repo_config)
    s.post(url, data=json.dumps(params), headers=headers)


def has_status(app, repo_config, repo_name, sha):
    url = get_api_url(app, repo_config, github_status_url).format(
        repo_name=repo_name,
        sha=sha)

    logging.debug("Getting status for %s %s", repo_name, sha)

    s = get_session_for_repo(app, repo_config)
    response = s.get(url)

    # The GitHub commit status API returns a JSON list, so `len()` checks
    # whether any statuses are set for the commit.
    return bool(len(response.json))


def register_github_hooks(app):
    with app.app_context():
        github_endpoint = "http://%s%s" % (
                app.config.get("GITHUB_NOTIFICATION_SERVER_NAME",
                               app.config["SERVER_NAME"]),
                url_for("base.github_notification", _external=False))

    for repo_config in app.config["REPOSITORIES"]:
        repo_name = repo_config["github_repo"]
        url = get_api_url(app, repo_config, github_hooks_url).format(
            repo_name=repo_name)

        s = get_session_for_repo(app, repo_config)
        response = s.get(url)

        if not response.ok:
            logging.warn("Unable to look up GitHub hooks for repo %s "
                         "with url %s: %s %s",
                         repo_name, github_endpoint, response.status_code,
                         response.reason)
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

            response = s.post(url, data=json.dumps(params), headers=headers)

            if response.ok:
                logging.info("Registered github hook for %s: %s",
                             repo_name, github_endpoint)
            else:
                logging.error("Unable to register github hook for %s: %s",
                              repo_name, response.status_code)
