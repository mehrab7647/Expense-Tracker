"""Setup script for Expense Tracker application."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

setup(
    name="expense-tracker",
    version="1.0.0",
    author="Expense Tracker Team",
    author_email="contact@expensetracker.com",
    description="A comprehensive personal finance management system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/expense-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Accounting",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core functionality has no external dependencies
    ],
    extras_require={
        "full": [
            "matplotlib>=3.5.0",
            "openpyxl>=3.0.0",
            "Pillow>=8.0.0",
        ],
        "charts": ["matplotlib>=3.5.0"],
        "excel": ["openpyxl>=3.0.0"],
        "gui": ["Pillow>=8.0.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "flake8>=4.0.0",
            "black>=22.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "expense-tracker=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "expense_tracker": ["*.json", "*.txt"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/expense-tracker/issues",
        "Source": "https://github.com/yourusername/expense-tracker",
        "Documentation": "https://github.com/yourusername/expense-tracker/wiki",
    },
)