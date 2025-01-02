from setuptools import setup, find_packages

setup(
    name="youtube_scraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'google-api-python-client',
        'python-dotenv',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'textblob',
        'loguru',
        'pytest',
        'requests'
    ],
    python_requires='>=3.8',
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive YouTube data scraping and analysis tool",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/youtube_scraper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
