#!/usr/bin/env python3
"""
Setup script for NFL Fantasy League CLI
"""

from setuptools import setup, find_packages

setup(
    name="nfl-fantasy-cli",
    version="1.0.0",
    description="NFL Fantasy League Command Line Interface",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.0.5",
        "psycopg[binary]==3.2.3",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "cachetools==5.3.1",
        "click==8.1.7",
        "rich==13.5.2",
        "tabulate==0.9.0",
    ],
    entry_points={
        'console_scripts': [
            'fantasy-cli=nfl_fantasy_cli.cli:cli',
        ],
    },
    python_requires=">=3.8",
)
