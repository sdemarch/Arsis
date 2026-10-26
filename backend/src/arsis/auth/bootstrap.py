"""Create the first Arsis responsible from an interactive local command."""

import argparse
import getpass
from collections.abc import Sequence

from arsis.auth.service import bootstrap_first_responsible
from arsis.core.database import get_session_factory
from arsis.core.errors import ConflictError


def _parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True, help="Email del primo responsabile")
    parser.add_argument("--display-name", required=True, help="Nome mostrato nell'applicazione")
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> None:
    options = _parse_args(arguments)
    password = getpass.getpass("Password (minimo 12 caratteri): ")
    confirmation = getpass.getpass("Conferma password: ")
    if password != confirmation:
        raise SystemExit("Le password non coincidono")

    try:
        with get_session_factory()() as session:
            user = bootstrap_first_responsible(
                session,
                email=options.email,
                display_name=options.display_name,
                password=password,
            )
    except (ConflictError, ValueError) as exception:
        raise SystemExit(str(exception)) from exception

    print(f"Primo responsabile creato: {user.display_name} <{user.email}>")


if __name__ == "__main__":
    main()
