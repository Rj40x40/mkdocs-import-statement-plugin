from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup (
    name='mkdocs-import-statement-plugin',
    author='Rj40x40',
    author_email='Rj40x40dev@gmail.com',
    # maintainer='Rj40x40',
    # maintainer_email='Rj40x40dev@gmail.com',
    description="MkDocs plugin to insert images and tables from files into markdown.",
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    url="https://github.com/Rj40x40/mkdocs-import-statement-plugin/",
    version='23.1.4',
    # download_url=DOWNLOAD_URL,
    python_requires='>=3.6',
    install_requires=["mkdocs>=1.4"],
    # extras_require=EXTRAS_REQUIRE,
    packages=['mkdocs_import_statement_plugin'],
    # classifiers=CLASSIFIERS
    entry_points={
        'mkdocs.plugins': [
            'import-statement = mkdocs_import_statement_plugin.plugin:ImportPlugin',
        ]
    },
)
