# Leeroy: Jenkins integration with GitHub pull requests

Leeroy is a Python [Flask](http://flask.pocoo.org) service which
integrates Jenkins with GitHub pull requests.  Leeroy uses [GitHub
hooks](http://developer.github.com/v3/repos/hooks/) to listen for pull
request notifications and starts jobs on your Jenkins server.  Using the
Jenkins [notification plugin][jnp], Leeroy updates the pull request using
GitHub's [status API](http://developer.github.com/v3/repos/statuses/)
with pending, success, failure, or error statuses.

## Installation

Install the package using pip:

    $ pip install leeroy

## Configuration

Leeroy needs to be configured to point to your GitHub repositories,
to your Jenkins server and its jobs.  Leeroy will attempt to automatically
install the GitHub hook for you.  You will also need to configure your
Jenkins jobs to pull the right repositories and commits.

### Leeroy Configuration

You may either edit the `leeroy/settings.py` file or create a new file and
set the `LEEROY_CONFIG` environment variable to point to that file.  It
should look something like:

[embedmd]:# (leeroy/settings.py python)
```python
DEBUG = True
LOGGING_CONF = "logging.conf"
LOGGER_NAME = "leeroy"

# The hostname (and :port, if necessary) of this server
SERVER_NAME = "leeroy.example.com"

# The hostname (and :port, if necessary) of the server GitHub should send
# notification to. It can be different from SERVER_NAME when another server is
# proxying requests to leeroy.  Falls back to SERVER_NAME if not provided.
# GITHUB_NOTIFICATION_SERVER_NAME = "leeroy.example.com"
# GITHUB_NOTIFICATION_SERVER_SCHEME = "http"

# GitHub configuration
# The base URL for GitHub's API. If using GitHub Enterprise, change this to
# https://servername/api/v3
# GITHUB_API_BASE = "https://github.example.com/api/v3"
GITHUB_API_BASE = "https://api.github.com"

# Verify SSL certificate. Always set this to True unless using GitHub
# Enterprise with a self signed certificate.
GITHUB_VERIFY = True

# Verify SSL certificate for Jenkins server. Always set this to True unless
# using Jenkins with a self signed certificate. Optionally use a path
# to the Jenkins CA bundle.
# JENKINS_VERIFY = "/etc/nginx/ssl/"
JENKINS_VERIFY = True

# Create and use a GitHub API token or supply a user and password.
GITHUB_TOKEN = ""
# GITHUB_USER = "octocat"
# GITHUB_PASSWORD = ""

# GitHub build context
GITHUB_CONTEXT = "leeroy/jenkins"

# Register per-repo webhooks.  Defaults to true
GITHUB_REGISTER_REPO_HOOKS = True

# Jenkins configuration
# JENKINS_USER and JENKINS_PASSWORD assume you're using basic HTTP
# authentication, not Jenkins's built in auth system.
# JENKINS_BUILD_TOKEN can be used with the "Trigger builds remotely"
# build trigger configuration
JENKINS_URL = "https://jenkins.example.com"
JENKINS_USER = ""
JENKINS_PASSWORD = ""
JENKINS_BUILD_TOKEN = None

# Use the Build Authorization Token Root Plugin's alternative URL for
# triggering builds.  Handy when using build tokens and no
# authentication.
JENKINS_AUTH_TOKEN_ROOT_BUILD = False

# Whether a Jenkins job is created for each commit in a pull request,
# or only one for the last one.
# What commits to build in a pull request. There are three options:
# 'ALL': build all commits in the pull request.
# 'LAST': build only the last commit in the pull request.
# 'NEW': build only commits that don't already have a commit status set.
#        (default)
BUILD_COMMITS = 'NEW'

# A list of dicts containing configuration for each GitHub repository &
# Jenkins job pair you want to join together.
#
# An example entry:
#
# {"github_repo": "litl/leeroy",
#  "jenkins_job_name": "leeroy-github",
#  "github_api_base": "https://github.example.com/api/v3",
#  "github_token": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
#  "github_user": "litl",
#  "github_password": "password",
#  "github_context": "leeroy",
#  "jenkins_url": ""https://jenkins2.example.com"",
#  "jenkins_user": "litl",
#  "jenkins_password": "password",
#  "jenkins_build_token": "abc123",
#  "build_commits": "LAST"}
#
# github_api_base, github_token, github_user, github_password, jenkins_url,
# jenkins_user, jenkins_password, and build_commits are optional.  If not
# present, they'll pull from the toplevel configuration options (GITHUB_USER,
# etc.)
REPOSITORIES = [
    {"github_repo": "litl/leeroy",
     "jenkins_job_name": "leeroy-github"}
]
```

### Jenkins Configuration

1. Install the Jenkins [git plugin][jgp] and [notification plugin][jnp].

2. Create a Jenkins job.  Under "Job Notifications", set a Notification
Endpoint with protocol HTTP and the URL pointing to `/notification/jenkins`
on your Leeroy server.  If your Leeroy server is `leeroy.example.com`, set
this to `http://leeroy.example.com/notification/jenkins`.

3. Check the "This build is parameterized" checkbox, and add 4 string
parameters: `GIT_BASE_REPO`, `GIT_HEAD_REPO`, `GIT_SHA1`, and `GITHUB_URL`.
Default values like `username/repo` for `GIT_BASE_REPO` and `GIT_HEAD_REPO`,
and `master` for `GIT_SHA1` are a good idea, but not required.

4. Under "Source Code Management", select Git.  Set the "Repository URL" to
`git@github.com:$GIT_HEAD_REPO.git`.  Set "Branch Specifier" to `$GIT_SHA1`.

5. Configure the rest of the job however you would otherwise.

[jgp]: https://wiki.jenkins-ci.org/display/JENKINS/Git+Plugin
[jnp]: https://wiki.jenkins-ci.org/display/JENKINS/Notification+Plugin

## Running Leeroy

After configuring your service, you can start Leeroy:

    $ uwsgi uwsgi.ini

Ensure that the GitHub hook has been installed by visiting
`https://github.com/<user>/<repo>/admin/hooks` for your project, or by
checking the Leeroy logs.

Submit a pull request for one of your watched GitHub repositories.  You
should shortly see a build scheduled for its corresponding Jenkins job.
Soon after that, you should see a "pending" status on the pull request
in GitHub.  Once the build finishes, you should see either a "success"
or "failure" status on your pull request.  Congratulations!

A `Procfile` is included so you can easily run Leeroy on Heroku.

## Cron task to fix missing statuses

Sometimes Github doesn't fire a hook, or Jenkins forgets to build a job.  You
can take care of this wonderful edge-case by running the following in a
cron-task:

    $ leeroy-cron

You can add it to your crontab to run at whatever interval suits you.

## Commandline tool to (re)try pull requests

Sometimes you want to replay a pull-request job.  Maybe the status failed
eratically.  Maybe you don't have the Jenkins Rebuild plugin.  Whatever your
reason you can try:

    $ leeroy-retry foo/bar 1234

And leeroy will re-test pull request 1234 in the foo/bar

## Contribution

Contributions are welcome!  Here's the best way to do that:

1. Fork the repo
2. Make your changes, preferably in a feature branch on your repo.  Don't
forget to update the AUTHORS.md file!
3. Submit a pull request

Please make sure that `python setup.py flake8` does not return any PEP-8 or
pyflakes errors before submitting your pull request.

## FAQ

### Why is this a server instead of a Jenkins plugin?

The honest answer is that I spend most of my day developing a Flask
application in Python, and that's the environment I have set up, feel
very comfortable in, and where I knew I could get something up and
running quickly.

The delusional answer is that this makes it possible to integrate
other CI services fairly easily in the future.

### What's with the name Leeroy?

[Know your meme.](http://knowyourmeme.com/memes/leeroy-jenkins)

## Copyright and License

Leeroy is Copyright (c) 2012 litl, LLC and licensed under the MIT license.
See the LICENSE file for full details.
