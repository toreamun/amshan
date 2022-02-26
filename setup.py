"""Python package setup."""
import setuptools

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="amshan",
    version="2.0.3",
    author="Tore Amundsen",
    author_email="tore@amundsen.org",
    description="Decode P1 and MBUS (Meter Bus) DLMS data. Special support for norwegian and swedish meters.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=["POSIX", "Windows"],
    url="https://github.com/toreamun/amshan",
    packages=["han"],
    package_data={"han": ["py.typed"]},
    keywords=[
        "meter",
        "han",
        "ams",
        "p1",
        "mbus",
        "aidon",
        "kaifa",
        "kamstrup",
        "dlms",
        "cosem",
        "hdlc",
        "fast frame check",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["construct"],
    extras_require={"serial": ["pyserial-asyncio>=0.4"]},
)
