from setuptools import setup, find_packages

setup(
    name="gpt_cost_estimator",
    version="0.6",
    packages=find_packages(),
    install_requires=[
        "tiktoken",
        "openai",
        "tqdm",
        "lorem_text"
    ],
    author="Michael Achmann",
    author_email="michael.achmann@informatik.uni-regensburg.de",
    description="A cost estimator for OpenAI API calls in tqdm loops.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/michaelachmann/gpt-cost-estimator/",
)
