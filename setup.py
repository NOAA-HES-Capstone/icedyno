"""
Pixi does not currently support editable installations of projects. In order to do so and preserve the pixi.toml as the single source
of truth for project dependencies, pip needs to be added as a dependency and a setup.py needs to scrap the pixi.toml for the dep list.

https://github.com/prefix-dev/pixi/issues/175
https://github.com/prefix-dev/pixi/issues/79

To have an editable installation of icedyno, run:
``pixi install pip -e .``
"""
import toml
from setuptools import find_packages, setup

# Allow the pixi.toml to be the single source of truth for dependencies
with open("pixi.toml", "r") as file:
    pixi_config = toml.load(file)

# Extract the dependencies
dependencies = pixi_config["dependencies"]

# Convert dependencies to a format suitable for setup.py
install_requires = [
    f"{pkg}>={dependencies[pkg].split(',')[0].replace('>=','')}" for pkg in dependencies
]


setup(
    name="icedyno",
    version=pixi_config["project"]["version"],
    description=pixi_config["project"]["description"],
    author="Julieanna Bacon, Soolu Thomas, Brendon Gory, Matthew Thanos, Ruchi Asthana",
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
