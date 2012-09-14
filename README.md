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

```python

DEBUG = True
LOGGING_CONF = "logging.conf"
LOGGER_NAME = "leeroy"

# The hostname (and :port, if necessary) of this server, used for
# the GitHub hook
SERVER_NAME = "leeroy.example.com"

# GitHub configuration
GITHUB_USER = "octocat"
GITHUB_PASSWORD = ""

# Jenkins configuration
JENKINS_URL = "https://jenkins.example.com"
JENKINS_USER = "hudson"
JENKINS_PASSWORD = ""

# Whether a Jenkins job is created for each commit in a pull request,
# or only one for the last one.
BUILD_ALL_COMMITS = True

# A list of dicts containing configuration for each GitHub repository &
# Jenkins job pair you want to join together.
#
# An example entry:
#
# {"github_repo": "litl/leeroy",
#  "jenkins_job_name": "leeroy-github",
#  "github_user": "litl",
#  "github_password": "password",
#  "jenkins_user": "litl",
#  "jenkins_password": "password",
#  "build_all_commits": False}
#
# github_user, github_password, jenkins_user, jenkins_password, and
# build_all_commits are optional.  If not present, they'll pull from
# the toplevel configuration options (GITHUB_USER, etc.)
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

    $ leeroy

Ensure that the GitHub hook has been installed by visiting
`https://github.com/<user>/<repo>/admin/hooks` for your project, or by
checking the Leeroy logs.

Submit a pull request for one of your watched GitHub repositories.  You
should shortly see a build scheduled for its corresponding Jenkins job.
Soon after that, you should see a "pending" status on the pull request
in GitHub.  Once the build finishes, you should see either a "success"
or "failure" status on your pull request.  Congratulations!

If you want to run Leeroy in a more production-ready environment then any
WSGI app server should work.  We are fans of
[uwsgi](http://projects.unbit.it/uwsgi/).

## Contribution

Contributions are welcome!  Here's the best way to do that:

1. Fork the repo
2. Make your changes, preferably in a feature branch on your repo.  Don't
forget to update the AUTHORS.md file!
3. Submit a pull request

Please make sure that `python setup.py test` does not return any PEP-8 or
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
