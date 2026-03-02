#!/usr/bin/env python3
"""
My Lenguaje - Setup
Instalación como paquete Python
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

requirements = []
req_file = this_directory / "requirements.txt"
if req_file.exists():
    requirements = [
        line.strip() 
        for line in req_file.read_text().split('\n') 
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="my-lenguaje",
    version="0.6.5",
    author="Tu Nombre",
    author_email="tu-email@ejemplo.com",
    description="Un lenguaje de programación en español con características enterprise",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/my-lenguaje",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Languages",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Natural Language :: Spanish",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'my=my:main',
            'my-lenguaje=my:main',
        ],
    },
    keywords=['lenguaje', 'español', 'programming language', 'spanish'],
)
