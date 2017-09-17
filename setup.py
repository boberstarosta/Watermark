from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["data/*"]

setup(
    name = "watermark",
    version = "1.0",
    description = "Adding watermarks to images",
    author = "Bober",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['watermark'],
    package_data = {"watermark" : files },
    scripts = ["run.py", "run.pyw"],
    long_description = """Really long text here.""" 
)
