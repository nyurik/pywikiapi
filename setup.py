"""Setup script for pywikiapi"""

import os.path
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as fid:
    README = fid.read()

setup(
    name="pywikiapi",
    version="1.0.2",
    description="Tiny MediaWiki API client library from the author of the MW API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/nyurik/pywikiapi",
    author="Yuri Astrakhan",
    author_email="YuriAstrakhan@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=["pywikiapi"],
    include_package_data=True,
    install_requires=[
        "importlib_resources", "typing", 'requests'
    ],
    entry_points={"console_scripts": ["pywikiapi=reader.__main__:main"]},
)
