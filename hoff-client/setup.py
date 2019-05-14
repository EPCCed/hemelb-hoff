from setuptools import setup

setup(
    name="hoff-client",
    version="0.1.0",
    author="Rupert Nash",
    author_email="r.nash@epcc.ed.ac.uk",
    description="HemeLB offload client",
    namespace_packages=["hoff"],
    packages=[
        "hoff",
        "hoff.client",
        "hoff.client.cmdline",
        "hoff.client.cmdline.job",
        "hoff.client.cmdline.job.ls",
        "hoff.client.cmdline.job.rm",
        "hoff.client.cmdline.output",
        "hoff.client.cmdline.output.cp",
        "hoff.client.cmdline.output.ls",
    ],
    install_requires=["requests"],
    entry_points={
        "console_scripts": ["hoff = hoff.client.cmdline:main"]
    },
)
