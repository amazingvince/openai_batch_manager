# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openai-batch-manager",
    version="0.1.0",
    author="Vincent Haines",
    author_email="amazingvince@gmail.com",
    description="A tool to manage OpenAI batch processing for large JSONL files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amazingvince/openai_batch_manager",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "httpx",
        "asyncio",
        "tqdm",
        "python-dotenv",
        "tenacity",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "openai-batch-manager=openai_batch_manager.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
