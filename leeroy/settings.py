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
