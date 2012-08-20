from setuptools import setup

setup(
	name="Agentum",
	description="Multiagent modeling toolkit",
	version="0.1",
	author="Alex Kouznetsov, Max Tsvetovat",
	packages=['agentum', 'agentum.sim'],
	install_requires=[
        'setuptools',
        'simplejson',
	],
)