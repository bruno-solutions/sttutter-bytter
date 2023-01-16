from setuptools import setup

from configuration.constants import APPLICATION_NAME, APPLICATION_VERSION, APPLICATION_URL, APPLICATION_AUTHOR, APPLICATION_EMAIL, APPLICATION_DESCRIPTION

setup(
    name=APPLICATION_NAME,
    version=APPLICATION_VERSION,
    url=APPLICATION_URL,
    author=APPLICATION_AUTHOR,
    author_email=APPLICATION_EMAIL,
    description=APPLICATION_DESCRIPTION,
    license="MIT",
    package_dir={"": "app"},
    packages=["loader", "logger", "slicer", "tagger", "tester", "audioprocessor"]
)
