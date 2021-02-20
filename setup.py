#!/usr/bin/env python3
import os
import setuptools

version = {}
with open("mllp_http/version.py", "r") as f:
    exec(f.read(), version)

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    author="Rivet Health",
    author_email="ops@rivethealth.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    description="Translate between MLLP and HTTP",
    entry_points={
        "console_scripts": [
            "mllp2http=mllp_http.main:mllp2http",
            "http2mllp=mllp_http.main:http2mllp",
        ]
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["requests"],
    name="mllp-http",
    packages=setuptools.find_packages(),
    project_urls={
        "Issues": "https://github.com/rivethealth/mllp-http/issues",
    },
    url="https://github.com/rivethealth/mllp-http",
    version=version["__version__"],
)
