# Copyright 2012 litl, LLC.  Licensed under the MIT license.

import requests

build_path = "/job/{job_name}/buildWithParameters?" \
    "GIT_REPO={git_repo}&GIT_SHA1={git_sha1}&GITHUB_URL={github_url}"


def get_jenkins_auth(app, repo_config):
    user = repo_config.get("jenkins_user",
                           app.config["JENKINS_USER"])
    password = repo_config.get("jenkins_password",
                               app.config["JENKINS_PASSWORD"])

    return user, password


def schedule_build(app, repo_config, repo_name, sha, html_url):
    job_name = repo_config["jenkins_job_name"]

    url = app.config["JENKINS_URL"] + \
        build_path.format(job_name=job_name,
                          git_repo=repo_name,
                          git_sha1=sha,
                          github_url=html_url)

    requests.get(url, auth=get_jenkins_auth(app, repo_config))
