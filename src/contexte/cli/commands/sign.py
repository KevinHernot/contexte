"""`ctx sign` command."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from contexte.cli.console import console, fail


def register(app: typer.Typer) -> None:
    @app.command("sign")
    def sign_cmd(
        pack: Annotated[Path, typer.Argument(help="Input .ctxpack path.")],
        key: Annotated[Path, typer.Option("--key", help="Path to private key.")] = None,
        gen_key: Annotated[
            bool, typer.Option("--gen-key", help="Generate a new key pair.")
        ] = False,
        output_dir: Annotated[
            Path, typer.Option("--output-dir", help="Directory for generated keys.")
        ] = Path("."),
    ) -> None:
        """Sign a context pack manifest using Ed25519."""
        from contexte.core.signing import generate_key_pair, sign_data
        from contexte.pack.reader import PackReader
        from contexte.pack.layout import SIGNATURE_JSON
        from contexte.ir.serialize import write_json
        import zipfile
        import shutil

        if gen_key:
            priv, pub = generate_key_pair(output_dir)
            console.print(f"Generated key pair:\n  Private: [bold]{priv}[/bold]\n  Public: [bold]{pub}[/bold]")
            if not key:
                key = priv

        if not key:
            fail(ValueError("--key is required for signing unless --gen-key is used."))

        try:
            reader = PackReader(pack)
            manifest_bytes = reader.read_member_text("manifest.json").encode("utf-8")
            signature = sign_data(manifest_bytes, key)
            
            # We need to add the signature.json to the existing ZIP.
            # ZIP format doesn't support easy 'add', so we'll do it safely.
            temp_pack = pack.with_suffix(".tmp_sign")
            shutil.copy2(pack, temp_pack)
            with zipfile.ZipFile(temp_pack, "a") as archive:
                archive.writestr(SIGNATURE_JSON, f'{{"signature": "{signature}", "algorithm": "ed25519"}}')
            
            temp_pack.replace(pack)
            console.print(f"[green]Successfully signed {pack}[/green]")
        except Exception as exc:
            fail(exc)
