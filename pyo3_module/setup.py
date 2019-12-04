from setuptools import find_packages, setup

try:
    from setuptools_rust import RustExtension
except ImportError:
    import subprocess
    import sys

    errno = subprocess.call([sys.executable, "-m", "pip", "install", "setuptools-rust", "--user"])
    if errno:
        print("Please install setuptools-rust package")
        raise SystemExit(errno)
    else:
        from setuptools_rust import RustExtension

setup_requires = ['setuptools-rust>=0.10.2']
install_requires = ['numpy']

setup(
    name='atk_mod_rm',
    version='0.1.0',
    description='Example of python-extension using rust-numpy',
    rust_extensions=[RustExtension(
        'atk_mod_rm.atk_mod_rm',
        './Cargo.toml',
    )],
    install_requires=install_requires,
    setup_requires=setup_requires,
    packages=find_packages(),
    zip_safe=False,
)