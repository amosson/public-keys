from setuptools import setup, find_packages


setup(
    name="public_keychain",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(),
    python_requires=">=3.8.0",
)
