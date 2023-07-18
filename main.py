import importlib, requests, subprocess, sys, os
from urllib.parse import urlparse
from types import ModuleType

clear = lambda : os.system('cls||clear')

def is_not_installed (package: str) -> bool:
    """Returns True if a PyPI is not installed"""
    spec = importlib.util.find_spec(package)
    loweredSpec = importlib.util.find_spec(package.lower())
    if (spec is None) and (loweredSpec is None): 
        return True
    return False

def install_from_pypi (package: str) -> None:
    """Install a package from PyPI"""
    if is_not_installed(package):
        if package == "pip":
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        else:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def install_from_github (userOrOrganization: str, packages: list) -> None:
    """Install a package from github.com"""
    for package in packages:
        url = f"git+https://github.com/{userOrOrganization}/{package}.git#egg={package}"
        install_from_pypi(url)

def install (*packages: str) -> None:
    """Install packages from PyPI or github.com"""
    for package in packages:
        if "@" in package:
            userOrOrganization = package.split("@")[1]
            package_names = package.split("@")[0].split(",")
            install_from_github(userOrOrganization, package_names)
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
        with open(url[8:]) as f:
            result["content"] = f.read()
        result["origin"] = "local"
        result["name"] = url[8:].replace("/", "_").replace(":", "").replace(".", "_")[:-3]
    else:
        response = requests.get(url)
        result["content"] = response.text
        result["content_type"] = response.headers["Content-Type"]
        result["origin"] = "remote"
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname.split(".")[::-1]
        result["name"] = "_".join(hostname) + parsed_url.path.replace("/", "_").replace(".", "_")[:-3]
    return result

def require (url: str) -> ModuleType | None:
    """Returns a module from a url"""
    if not os.path.exists("modules"):
        os.mkdir("modules")
    r = get_code(url)
    with open(f"modules/{r['name']}.py", "w") as f:
        f.write(r["content"])
    try:
        module = __import__(f"modules.{r['name']}")
        return module
    except ModuleNotFoundError as e:
        print(f"{r['name']} requires package {e.name} to be installed")
        return None
