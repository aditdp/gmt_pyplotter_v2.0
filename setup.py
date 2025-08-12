from setuptools import setup, find_packages


setup(
    name="gmt_pyplotter",
    version="v2.0",
    description="Python customtkinter script to plot map with GMT with GUI",
    url="https://github.com/aditdp/gmt_pyplotter_v2.0",
    author="aditdp",
    author_email="adit015@brin.go.id",
    license="BRIN",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "gmt_pyplotter": [
            "data/*.png",
            "data/*.txt",
            "image/*.png",
            "image/*.jpg",
            "*json",
        ]
    },
    install_requires=[
        "setuptools",
        "Pillow",
        "customtkinter",
        "psutil",
        "CTkToolTip",
        "CTkColorPicker",
        "CTkMessagebox",
    ],
    include_package_data=True,
    entry_points={"console_scripts": ["gmt_pyplotter = gmt_pyplotter.main:main"]},
)
