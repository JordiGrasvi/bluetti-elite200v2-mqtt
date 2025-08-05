from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bluetti-elite200v2-mqtt",
    version="1.0.0",
    author="Bluetti Elite 200 V2 Community",
    description="MQTT bridge for Bluetti Elite 200 V2 power station",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JordiGrasvi/bluetti-elite200v2-mqtt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Home Automation",
        "Topic :: System :: Hardware",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bluetti-mqtt=bluetti_mqtt.server_cli:main",
            "bluetti-discovery=bluetti_mqtt.discovery_cli:main",
            "bluetti-logger=bluetti_mqtt.logger_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)