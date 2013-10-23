import logging
import time
import datetime
from leeroy import github
from leeroy.app import app
from leeroy.github import get_pull_requests, get_status
from leeroy.jenkins import schedule_build

__author__ = 'davedash'

# How old does a commit status need to be (in seconds) before we retry the
# request.
# If a URL isn't present, this indicates a job was never made. If a URL is
# present, this indicates a job may not have reported back to Leeroy.
MAX_AGE_PENDING_WITH_URL = 10 * 60
MAX_AGE_PENDING_WITHOUT_URL = 2 * 60

log = logging.getLogger(__name__)


def convert_to_age_in_seconds(last_status):
    updated_at = last_status.get('updated_at')
    fmt = '%Y-%m-%dT%H:%M:%SZ'
    update_at_in_seconds = time.mktime(
        datetime.datetime.strptime(updated_at, fmt).timetuple())
    age = time.time() - update_at_in_seconds
    return age


def retry_jenkins(repo_config, pull_request):
    pr_number = pull_request['number']
    html_url = pull_request["html_url"]
    sha = pull_request['head']['sha']
    log.debug("Creating a new Jenkins job for {0}".format(pr_number))
    head_repo_name, shas = github.get_commits(app, repo_config, pull_request)
    schedule_build(app, repo_config, head_repo_name, sha, html_url)


def main():
    for repo_config in app.config["REPOSITORIES"]:
        for pull_request in get_pull_requests(app, repo_config):
            sha = pull_request['head']['sha']
            repo_name = repo_config['github_repo']
            status_data = get_status(app, repo_config, repo_name, sha).json
            if status_data:
                last_status = status_data[0]
                status = last_status.get('state')
                if status == 'pending':
                    max_age = MAX_AGE_PENDING_WITHOUT_URL
                    if last_status.get('target_url'):
                        max_age = MAX_AGE_PENDING_WITH_URL

                    age = convert_to_age_in_seconds(last_status)
                    if age > max_age:
                        # Somewhat heavy, but it'll do
                        retry_jenkins(repo_config, pull_request)
            else:
                # Somewhat heavy, but it'll do
                retry_jenkins(repo_config, pull_request)


if __name__ == '__main__':
    main()
