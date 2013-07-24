# Copyright 2012 litl, LLC.  Licensed under the MIT license.

import logging
import requests

build_path = "/job/{job_name}/buildWithParameters"\
    "?GIT_BASE_REPO={git_base_repo}" \
    "&GIT_HEAD_REPO={git_head_repo}" \
    "&GIT_SHA1={git_sha1}" \
    "&GITHUB_URL={github_url}"


def get_jenkins_auth(app, repo_config):
    user = repo_config.get("jenkins_user",
                           app.config["JENKINS_USER"])
    password = repo_config.get("jenkins_password",
                               app.config["JENKINS_PASSWORD"])

    return user, password


def get_jenkins_url(app, repo_config):
    return repo_config.get("jenkins_url", app.config["JENKINS_URL"])


def schedule_build(app, repo_config, head_repo_name, sha, html_url):
    base_repo_name = repo_config["github_repo"]
    job_name = repo_config["jenkins_job_name"]

    url = get_jenkins_url(app, repo_config) + \
        build_path.format(job_name=job_name,
                          git_base_repo=base_repo_name,
                          git_head_repo=head_repo_name,
                          git_sha1=sha,
                          github_url=html_url)

    logging.debug("Requesting build from Jenkins: %s", url)
    response = requests.post(url, auth=get_jenkins_auth(app, repo_config))
    logging.debug("Jenkins responded with status code %s",
                  response.status_code)
