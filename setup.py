"""Setup script for pywikiapi"""

from pathlib import Path

from setuptools import setup, find_packages

setup(
    name="pywikiapi",
    version="4.1.1",
    description="Tiny MediaWiki API client library from the author of the MW API",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests",)),
    test_suite="tests",
    url="https://github.com/nyurik/pywikiapi",
    author="Yuri Astrakhan",
    author_email="YuriAstrakhan@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    include_package_data=True,
    install_requires=["requests", 'responses'],
)
