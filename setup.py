import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='smartmeterdecode-toreamun',
    version='0.1.2',
    author="Tore Amundsen",
    author_email="tore@amundsen.org",
    description="Decode smart meter data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms = ["POSIX", "Windows"],
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    keywords=[
        "meter",
        "han",
        "ams",
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
    python_requires='>=3.6',
    install_requires=['construct'],
)
