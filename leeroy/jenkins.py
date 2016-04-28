# Copyright 2012 litl, LLC.  Licensed under the MIT license.

import logging
import requests


normal_build_path = "/job/{job_name}/buildWithParameters"\
    "?GIT_BASE_REPO={git_base_repo}" \
    "&GIT_HEAD_REPO={git_head_repo}" \
    "&GIT_SHA1={git_sha1}" \
    "&GITHUB_URL={github_url}"


auth_token_root_build_path = "/buildByToken/buildWithParameters" \
    "?job={job_name}" \
    "&GIT_BASE_REPO={git_base_repo}" \
    "&GIT_HEAD_REPO={git_head_repo}" \
    "&GIT_SHA1={git_sha1}" \
    "&GITHUB_URL={github_url}"


def get_jenkins_auth(app, repo_config):
    user = repo_config.get("jenkins_user",
                           app.config["JENKINS_USER"])
    password = repo_config.get("jenkins_password",
                               app.config["JENKINS_PASSWORD"])

    if not user:
        return None

    return user, password


def get_jenkins_url(app, repo_config):
    return repo_config.get("jenkins_url", app.config["JENKINS_URL"])


def schedule_build(app, repo_config, head_repo_name, sha, html_url):
    base_repo_name = repo_config["github_repo"]
    job_name = repo_config["jenkins_job_name"]

    if app.config.get("JENKINS_AUTH_TOKEN_ROOT_BUILD"):
        build_path = auth_token_root_build_path
    else:
        build_path = normal_build_path

    url = get_jenkins_url(app, repo_config) + \
        build_path.format(job_name=job_name,
                          git_base_repo=base_repo_name,
                          git_head_repo=head_repo_name,
                          git_sha1=sha,
                          github_url=html_url)

    build_token = repo_config.get("jenkins_build_token",
                                  app.config.get("JENKINS_BUILD_TOKEN"))
    if build_token is not None:
        url += "&token=" + build_token

    logging.debug("Requesting build from Jenkins: %s", url)
    response = requests.post(url,
                             auth=get_jenkins_auth(app, repo_config),
                             verify=app.config["JENKINS_VERIFY"],
                             allow_redirects=False)
    logging.debug("Jenkins responded with status code %s",
                  response.status_code)
    return response.status_code < 400

