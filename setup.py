"""Setup script for FlashGenie."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="flashgenie",
    version="0.1.0",
    author="FlashGenie Team",
    author_email="huckflower@gmail.com",
    description="A powerful and beginner-friendly flashcard app with spaced repetition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/himent12/FlashGenie",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "flashgenie=flashgenie.main:main",
        ],
    },
)
