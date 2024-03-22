import setuptools

setuptools.setup(
    name="jknowrob",
    version="0.0.1",
    author="Sascha Jongebloed",
    author_email="sasjonge@uni-bremen.de",
    description="A Jupyter Kernel for SWI-Prolog.",
    url="https://github.com/sasjonge/jupyer-knowrob.git",
    packages=setuptools.find_packages(),
    install_requires=[
        "pyswip",
        "ipykernel"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['jknowrobkernel=jknowrob.jupyter:main'],
    }
)
