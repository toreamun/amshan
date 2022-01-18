"""Python package setup."""
import setuptools

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="amshan",
    version="1.0.2",
    author="Tore Amundsen",
    author_email="tore@amundsen.org",
    description="Decode MBUS (Meter Bus) data with special support for norwegian AMS-smart meters (HAN port)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=["POSIX", "Windows"],
    url="https://github.com/toreamun/amshan",
    packages=["amshan"],
    package_data={"amshan": ["py.typed"]},
    keywords=[
        "meter",
        "han",
        "ams",
        "mbus",
        "aidon",
        "kaifa",
        "kamstrup",
        "cosem",
        "hdlc",
        "fast frame check",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["construct"],
    extras_require={"serial": ["pyserial-asyncio>=0.4"]},
)
