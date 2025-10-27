from setuptools import setup, find_packages

setup(
    name="ai-sarva",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'pandas==2.2.2',
        'numpy==1.26.4',
        'yfinance==0.2.43',
        'requests==2.32.3',
        'beautifulsoup4==4.12.3',
        'newspaper3k==0.2.8',
        'torch==2.4.1',
        'transformers==4.44.2',
        'rich==13.8.0',
        'pandas_ta==0.3.14',
        'python-dotenv==1.0.1',
    ],
    entry_points={
        'console_scripts': [
            'ai-sarva=src.main:main',
        ],
    },
    author="sayyah",
    description="AI-powered cryptocurrency trading signal generator",
    url="https://github.com/sayyah/AI-Sarva",
)
