# -*- coding: utf-8 -*-
import codecs
import os
import re
from distutils.core import setup

from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))


def find_version(*parts):
    """
    Figure out version number without importing the package.
    https://packaging.python.org/guides/single-sourcing-package-version/
    """
    with codecs.open(os.path.join(here, *parts), "r", errors="ignore") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"](.*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = find_version("revolut_merchant", "__init__.py")

setup(
    name="revolut-merchant-python",
    version=version,
    description="Revolut Merchant API client for Python",
    url="https://github.com/the-veloper/revolut-merchant-python/",
    long_description=open("README.md", "rb").read().decode("utf-8"),
    install_requires=open("requirements.txt", "r").read().splitlines(),
    tests_require=open("test_requirements.txt", "r").read().splitlines(),
    setup_requires=[
        "pytest-runner",
    ],
    packages=find_packages(".", exclude=["tests"]),
    include_package_data=True,
    author="Georgi Georgiev",
    author_email="g.georgiev@theorigamicorporation.com",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="revolut payments merchant api client",
    test_suite="tests",
)
