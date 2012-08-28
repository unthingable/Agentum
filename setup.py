from setuptools import setup

setup(
	name="Agentum",
	description="Multiagent modeling toolkit",
	version="0.1",
	author="Alex Kouznetsov, Max Tsvetovat",
	packages=['agentum'],
	install_requires=[
        'setuptools',
#        'simplejson',
	],
    entry_points = """
        [console_scripts]
        agentum = agentum.runner:run_main
    """
)
