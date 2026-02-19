import asyncio
import os
import subprocess
import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_py import build_py
from distutils.command.install import install


# from octobot_script import PROJECT_NAME, VERSION
# todo figure out how not to import octobot_script.__init__.py here
PROJECT_NAME = "OctoBot-Script"
VERSION = "0.0.30"  # major.minor.revision

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIST = os.path.join(
    ROOT_DIR, "octobot_script", "resources", "report", "dist", "index.html"
)


def _build_report():
    npm = "npm"

    print("[report] Installing JS dependencies…")
    result = subprocess.run(
        [npm, "install", "--prefer-offline"],
        cwd=ROOT_DIR,
        check=False,
    )
    if result.returncode != 0:
        print("[report] 'npm install' failed – skipping JS build.", file=sys.stderr)
        return

    print("[report] Building React bundle…")
    result = subprocess.run(
        [npm, "run", "build"],
        cwd=ROOT_DIR,
        check=False,
    )
    if result.returncode != 0:
        print("[report] 'npm run build' failed – skipping JS bundle.", file=sys.stderr)
        return

    if os.path.isfile(REPORT_DIST):
        print(f"[report] Built successfully → {REPORT_DIST}")
    else:
        print("[report] Build finished but dist/index.html not found.", file=sys.stderr)


class BuildPyWithReport(build_py):
    def run(self):
        _build_report()
        super().run()


def _post_install():
    import octobot_script.cli
    asyncio.run(octobot_script.cli.install_all_tentacles(True))


class InstallWithPostInstallAction(install):
    def run(self):
        install.run(self)
        self.execute(_post_install, (), msg="Installing OctoBot-Script tentacles")


PACKAGES = find_packages(
    exclude=[
        "tests",
        "octobot_script.imports*",
        "octobot_script.user*",
    ]
)

# long description from README file
with open('README.md', encoding='utf-8') as f:
    DESCRIPTION = f.read()

REQUIRED = open('requirements.txt').readlines()
REQUIRES_PYTHON = '>=3.8'

setup(
    name=PROJECT_NAME.lower().replace("-", "_"),
    version=VERSION,
    url='https://github.com/Drakkar-Software/OctoBot-Script',
    license='GPL-3.0',
    author='Drakkar-Software',
    author_email='contact@drakkar.software',
    description='Backtesting framework of the OctoBot Ecosystem',
    packages=PACKAGES,
    cmdclass={
        'install': InstallWithPostInstallAction,
        'build_py': BuildPyWithReport,
    },
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    tests_require=["pytest"],
    test_suite="tests",
    zip_safe=False,
    data_files=[],
    include_package_data=True,  # copy non python files on install
    install_requires=REQUIRED,
    python_requires=REQUIRES_PYTHON,
    entry_points={
        'console_scripts': [
            'octobot_script = octobot_script.cli:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.10',
    ],
)
