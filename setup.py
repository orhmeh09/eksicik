from distutils.core import setup

setup(name = "eksicik",
    version = "100",
    description = "eksi sozluk icin isvicre cakisi",
    author = "nrs",
    author_email = "onur@kreix.com",
    url = "https://github.com/nrs",
    packages = ['eksicik'],
    package_data = {'eksicik' : ["eksicik/*.py"]},
    scripts = ["bin/eksicik"],
    #long_description = """Really long text here."""
)
