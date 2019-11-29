# This script generates config.ini for setup.iss script
from dvc import __version__
import configparser as ConfigParser

config = ConfigParser.ConfigParser()
config.add_section("Version")
config.set("Version", "Version", __version__)

with open("scripts/innosetup/config.ini", "w") as f:
    config.write(f)
