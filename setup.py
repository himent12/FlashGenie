"""Setup script for FlashGenie."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="flashgenie",
    version="1.6.0",
    author="FlashGenie Team",
    author_email="huckflower@gmail.com",
    description="Intelligent flashcard application with adaptive spaced repetition and smart tagging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/himent12/FlashGenie",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    keywords="flashcards spaced-repetition learning education study memory ai smart-tagging",
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "flashgenie=flashgenie.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "flashgenie": ["assets/sample_data/*"],
    },
    project_urls={
        "Bug Reports": "https://github.com/himent12/FlashGenie/issues",
        "Source": "https://github.com/himent12/FlashGenie",
        "Documentation": "https://github.com/himent12/FlashGenie/blob/main/docs/user_guide.md",
    },
)
