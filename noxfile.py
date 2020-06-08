import tempfile

import nox

nox.options.sessions = "lint", "tests", "safety"


@nox.session(python=["3.8"])
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("pytest", "--cov")


locations = ["src", "tests", "noxfile.py"]


@nox.session(python=["3.8"])
def lint(session):
    args = session.posargs or locations
    session.install("flake8", "flake8-bugbear", "flake8-bandit", "flake8-import-order")
    session.run("flake8", *args)


@nox.session(python="3.8")
def black(session):
    args = session.posargs or locations
    args.insert(0, "-l 119")
    session.install("black")
    session.run("black", *args)


@nox.session(python="3.8")
def safety(session):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install("safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")
