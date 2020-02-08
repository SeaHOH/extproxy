#!/usr/bin/env python

import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read_file(path):
    with open(os.path.join(here, path), "r") as fp:
        return fp.read()

def get_version():
    content = read_file(os.path.join(package_name, "__init__.py"))
    version_match = re.search("^__version__ = ['\"]([^'\"]+)", content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

here = os.path.abspath(os.path.dirname(__file__))
package_name = "extproxy"
requires = ["PySocks>=1.7.1"]

setup(
    name="ExtProxy",
    version=get_version(),
    author="SeaHOH",
    author_email="seahoh@gmail.com",
    url="https://github.com/SeaHOH/extproxy",
    license="MIT",
    description=("ExtProxy extend urllib2's ProxyHandler to support "
                 "extra proxy types: HTTPS, SOCKS."),
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    keywords="urllib ProxyHandler HTTPS SOCKS proxy",
    packages=[package_name],
    install_requires=requires,
    zip_safe=True,
    platforms="any",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities"
    ],
    python_requires=">=2.7",
)