"""
pyrequire
Require python files from everywhere
"""

import importlib
from urllib.parse import urlparse
from types import ModuleType
import subprocess
import sys
import os
import requests

def clear () -> None:
    os.system('cls||clear')

def is_not_installed (package: str) -> bool:
    """Returns True if a PyPI is not installed"""
    spec = importlib.util.find_spec(package)
    lowered_spec = importlib.util.find_spec(package.lower())
    if (spec is None) and (lowered_spec is None): 
        return True
    return False

def install_from_pypi (package: str) -> None:
    """Install a package from PyPI"""
    if is_not_installed(package):
        if package == "pip":
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        else:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def install_from_github (user_or_organization: str, packages: list) -> None:
    """Install a package from github.com"""
    for package in packages:
        url = f"git+https://github.com/{user_or_organization}/{package}.git#egg={package}"
        install_from_pypi(url)

def install (*packages: str) -> None:
    """Install packages from PyPI or github.com"""
    for package in packages:
        if "@" in package:
            user_or_organization = package.split("@")[1]
            package_names = package.split("@")[0].split(",")
            install_from_github(user_or_organization, package_names)
        else:
            install_from_pypi(package)

def get_code (url: str) -> dict:
    """Returns the code of a file from a url"""
    result = {
        "content": "",
        "content_type": "text/plain; charset=utf-8",
        "origin": "",
        "name": ""
    }                 
    if url.startswith("file:///"):
        with open(url[8:], "r", encoding="utf-8") as file:
            result["content"] = file.read()
        result["origin"] = "local"
        result["name"] = url[8:].replace("/", "_").replace(":", "").replace(".", "_")[:-3]
    else:
        response = requests.get(url)
        result["content"] = response.text
        result["content_type"] = response.headers["Content-Type"]
        result["origin"] = "remote"
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname.split(".")[::-1]
        path = parsed_url.path.replace("/", "_").replace(".", "_")[:-3]
        result["name"] = "_".join(hostname) + path
    return result

def require (url: str) -> ModuleType or None:
    """Returns a module from a url"""
    if not os.path.exists("modules"):
        os.mkdir("modules")
    result = get_code(url)
    with open(f"modules/{result['name']}.py", "w", encoding="utf-8") as file:
        file.write(result["content"])
    try:
        module = __import__(f"modules.{result['name']}")
        return module
    except ModuleNotFoundError as error:
        print(f"{result['name']} requires package {error.name} to be installed")
        return None
