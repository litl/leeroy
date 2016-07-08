import os
import sys
from setuptools import setup, find_packages

VERSION = "0.3.0"


def get_requirements():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'requirements.txt')) as f:
        return [l.strip() for l in f]

setup(
    name="leeroy",
    version=VERSION,
    url="https://github.com/litl/leeroy",
    license="MIT",
    author="Joe Shaw",
    author_email="joeshaw@litl.com",
    description="Leeroy integrates Jenkins CI with GitHub pull requests",
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=get_requirements(),
    entry_points="""\
[console_scripts]
leeroy=leeroy.scripts:main
leeroy-cron=leeroy.cron:main
leeroy-retry=leeroy.retry:main
    """,
    packages=["leeroy"],
    setup_requires=['flake8'],
    classifiers=[
        # From http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        #"Development Status :: 6 - Mature",
        #"Development Status :: 7 - Inactive",
        "Environment :: Web Environment",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ]
)
