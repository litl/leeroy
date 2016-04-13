import argparse
import logging

from leeroy import github
from leeroy.app import app
from leeroy.github import BUILD_COMMITS_OPTIONS
from leeroy.jenkins import schedule_build

__author__ = 'davedash'

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', choices=[repo['github_repo'] for repo in
                                         app.config['REPOSITORIES']])
    parser.add_argument('pull_request', type=int)
    parser.add_argument('--commits', choices=BUILD_COMMITS_OPTIONS)
    args = parser.parse_args()

    log.info("Scheduling a build for PR {0}".format(args.pull_request))
    repo_config = github.get_repo_config(app, args.repo)
    pull_request = github.get_pull_request(app, repo_config, args.pull_request)
    head_repo_name, shas = github.get_commits(app, repo_config, pull_request,
                                              args.commits)
    html_url = pull_request["html_url"]
    for sha in shas:
        schedule_build(app, repo_config, head_repo_name, sha, html_url)

if __name__ == '__main__':
    main()
