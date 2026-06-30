from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="linkvault",
    version="1.0.0",
    description="A dependency-free CLI bookmark manager with tags, search, and dead-link checking.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NzJulien",
    url="https://github.com/NzJulien/linkvault",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.9",
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    entry_points={
        "console_scripts": [
            "linkvault=linkvault.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
