# PyInstaller spec for Arsis.exe. Run through scripts\build-windows.ps1, which
# compiles Angular first and prepares build\arsis.ico.
#
# One-folder build: faster start than one-file and what the installer copies.
# Bundled, read-only: the compiled frontend and the Liquibase changelog that
# arsis.core.migrations applies. User data never goes in here; it lives in
# %LOCALAPPDATA%\Arsis (see arsis.core.config.default_data_dir).

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH).parent  # noqa: F821 - provided by PyInstaller
ICON = ROOT / "build" / "arsis.ico"

analysis = Analysis(  # noqa: F821
    [str(ROOT / "packaging" / "launcher.py")],
    pathex=[str(ROOT / "backend" / "src")],
    datas=[
        (str(ROOT / "frontend" / "dist" / "arsis" / "browser"), "frontend"),
        (str(ROOT / "database" / "changelog"), "database/changelog"),
    ],
    # uvicorn picks its loop, protocol and lifespan implementations at runtime.
    hiddenimports=collect_submodules("uvicorn") + collect_submodules("arsis"),
    excludes=["tkinter", "pytest", "mypy", "ruff"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)  # noqa: F821
exe = EXE(  # noqa: F821
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="Arsis",
    console=False,
    icon=str(ICON) if ICON.is_file() else None,
    version=None,
)
COLLECT(  # noqa: F821
    exe,
    analysis.binaries,
    analysis.datas,
    name="Arsis",
)
