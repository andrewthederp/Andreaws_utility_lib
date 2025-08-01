from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
desc = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="andreaw_utilities",
    version="0.0.92",
    description="A library containing various utilities that I use in my projects.",
    long_description=desc,
    long_description_content_type="text/markdown",
    author="andreaw",
    url="https://github.com/andrewthederp/Andreaws_utility_lib",
    license="Apache",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    include_package_data=True,
    package_data={
        '': [
            'data/**',
        ]
    },
    python_requires=">=3.6",
    packages=find_packages(include=["utilities", "utilities.*"]),
)
