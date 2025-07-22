"""
Setup configuration for StudyBuddy AI Learning Assistant
Production-grade multi-agent system package
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "StudyBuddy AI Learning Assistant - Production multi-agent system"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(requirements_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Filter out comments and empty lines
    requirements = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)
    
    return requirements

setup(
    name="studybuddy",
    version="1.0.0",
    author="AI Workshop Team",
    author_email="team@aiworkshop.dev",
    description="Production multi-agent AI learning assistant powered by Qwen2.5-14B",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/aiworkshop/studybuddy",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "api": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
        ],
        "web": [
            "streamlit>=1.28.0",
        ],
        "gpu": [
            "torch>=2.0.0+cu118",
        ]
    },
    entry_points={
        "console_scripts": [
            "studybuddy-api=fastapi_app.main:main",
            "studybuddy-web=streamlit_app.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "studybuddy": [
            "config/*.yaml",
            "config/*.yml",
        ],
    },
    zip_safe=False,
    keywords="ai, education, learning, assistant, multi-agent, langchain, qwen",
    project_urls={
        "Bug Reports": "https://github.com/aiworkshop/studybuddy/issues",
        "Source": "https://github.com/aiworkshop/studybuddy",
        "Documentation": "https://studybuddy.aiworkshop.dev",
    },
)
