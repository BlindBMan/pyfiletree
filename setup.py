from setuptools import find_packages, setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pyfiletree',
    packages=find_packages(include=['pyfiletree']),
    version='0.1.6',
    description='Read/Write python files',
    author='Sam',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    extras_require={
      "dev": [
          "pytest>=4.4.1",
      ],
    },
    test_suite='tests',
    long_description=long_description,
    long_description_content_type='text/markdown'
)

# py setup.py bdist_wheel
# twine upload --repository testpypi dist/*
# twine upload dist/*
# pip install -e .
