from setuptools import setup
import os

from agentum import __version__


def local_file(fn):
    return open(os.path.join(os.path.dirname(__file__), fn))


with local_file('requirements.txt') as f:
    requirements = map(str.strip, f)


setup(
    name="Agentum",
    description="Agent-based modeling toolkit",
    version=__version__,
    author="Alex Kouznetsov, Max Tsvetovat",
    packages=['agentum'],
    install_requires=requirements,
    entry_points="""
        [console_scripts]
        agentum = agentum.runner:run_main
    """
)
