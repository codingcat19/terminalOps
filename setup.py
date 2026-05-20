from setuptools import setup


setup(
    name="terminalops",
    version="0.1.0",
    description="A terminal-first DevOps agent powered by Strands and Ollama.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    packages=["terminalops"],
    install_requires=[
        "psutil",
        "streamlit",
        "strands-agents[ollama]",
        "strands-agents-tools",
    ],
    scripts=["bin/terminalops"],
)
