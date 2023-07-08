from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in weekly_planner/__init__.py
from weekly_planner import __version__ as version

setup(
	name="weekly_planner",
	version=version,
	description="Weekly Planner for Monstessori Guides",
	author="Servio",
	author_email="ton@serviotech.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
