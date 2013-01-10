DEBUG = True
LOGGING_CONF = "logging.conf"
LOGGER_NAME = "leeroy"

# The hostname (and :port, if necessary) of this server
SERVER_NAME = "leeroy.example.com"

# The hostname (and :port, if necessary) of the server GitHub should send
# notification to. It can be different from SERVER_NAME when another server is
# proxying requests to leeroy.
GITHUB_NOTIFICATION_SERVER_NAME = SERVER_NAME

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

# Only accept Webhook POST requests that originate from these addresses. Set
# to something falsy to disable whitelisting.
WEBHOOK_ADDRESS_WHITELIST = [
    "127.0.0.1",
    # GitHub
    "207.97.227.253",
    "50.57.128.197",
    "108.171.174.178"
]

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
