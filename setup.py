"""
Setup configuration for Autonomous Scientific Research Agent
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="autonomous-scientific-agent",
    version="0.10.0",
    author="Research Team",
    author_email="support@example.com",
    description="A local multimodal LLM-based autonomous agent for scientific literature research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/user/autonomous-scientific-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "pylint>=2.17.0",
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "gpu": [
            "torch>=2.0.0,!=2.1.0",  # Avoid 2.1.0 due to bugs
            "flash-attn>=2.0.0",  # For faster inference
        ],
        "database": [
            "psycopg2-binary>=2.9.0",
            "pgvector>=0.1.0",
        ],
        "web": [
            "flask>=2.3.0",
            "flask-cors>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "autonomous-agent=src.core.orchestration:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "data/*"],
    },
    zip_safe=False,
)
