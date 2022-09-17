import setuptools

__version__ = "0.1.0"

setuptools.setup(
    name="django-bulk-copy",
    version=__version__,
    author="Ahmet Burak",
    author_email="ahmetbozyurtt@gmail.com",
    license="MIT",
    description="Write models to db with copy command.",
    url="https://github.com/ahmetveburak/django-bulk-copy",
    python_requires=">=3.6",
    install_requires=["django>=3.2", "psycopg2>=2.4.0"],
)
