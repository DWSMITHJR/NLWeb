from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="nlweb",
    version="0.1",
    packages=find_packages(include=['backend*']),
    package_dir={'': '.'},
    install_requires=requirements,
    python_requires='>=3.8',
    include_package_data=True,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'black>=21.5b2',
            'isort>=5.8.0',
            'mypy>=0.812',
        ],
    },
)
