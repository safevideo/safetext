import io
import os
import re

import setuptools


def get_long_description():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base_dir, "README.md"), encoding="utf-8") as f:
        return f.read()


def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def get_version():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(current_dir, "safetext", "__init__.py")
    with open(version_file, encoding="utf-8") as f:
        return re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', f.read(), re.M).group(1)


_DEV_REQUIREMENTS = [
    "black==21.7b0",
    "flake8==3.9.2",
    "isort==5.9.2",
    "click==8.0.4",
    "importlib-metadata>=1.1.0,<4.3;python_version<'3.8'",
]

extras = {"tests": _DEV_REQUIREMENTS, "dev": _DEV_REQUIREMENTS}

setuptools.setup(
    name="safetext",
    version=get_version(),
    author="",
    license="MIT",
    description="Rule-based profanity checking tool for English and Turkish.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/deepsafe/safetext",
    packages=setuptools.find_packages(exclude=["tests"]),
    python_requires=">=3.7",
    install_requires=get_requirements(),
    extras_require=extras,
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        "console_scripts": [
            "roboflow2huggingface=roboflow2huggingface.cli:app",
        ],
    },
    keywords="text, profanity, filtering, turkish, english",
)
