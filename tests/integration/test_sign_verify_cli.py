"""CLI integration tests for ``ctx sign`` and ``ctx verify``.

These tests exercise the user-visible commands end to end (typer CLI →
PackReader → cryptography), and pin the four behaviours we care about:

1. ``ctx sign`` writes ``signature.json`` into the pack.
2. ``ctx verify`` succeeds with the matching public key.
3. ``ctx verify`` fails when ``manifest.json`` has been tampered with.
4. ``ctx verify`` fails when a non-matching public key is supplied.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from typer.testing import CliRunner

from conftest import FIXTURES
from contexte.cli.app import app
from contexte.core.pipeline import build_context_pack
from contexte.pack.layout import MANIFEST, SIGNATURE_JSON

runner = CliRunner()


def _build_pack(tmp_path: Path) -> Path:
    pack = tmp_path / "test.ctxpack"
    build_context_pack(FIXTURES, pack, force=True, max_chars=800)
    return pack


def _gen_keys(tmp_path: Path, name: str = "contexte") -> tuple[Path, Path]:
    """Generate an Ed25519 keypair via the public signing API."""
    from contexte.core.signing import generate_key_pair

    keys_dir = tmp_path / f"{name}_keys"
    return generate_key_pair(keys_dir, name=name)


def test_ctx_sign_writes_signature_json(tmp_path: Path) -> None:
    pack = _build_pack(tmp_path)
    priv, _ = _gen_keys(tmp_path)

    result = runner.invoke(app, ["sign", str(pack), "--key", str(priv)])
    assert result.exit_code == 0, result.output
    assert "Successfully signed" in result.output

    with zipfile.ZipFile(pack) as archive:
        assert SIGNATURE_JSON in archive.namelist()
        payload = json.loads(archive.read(SIGNATURE_JSON))
        assert payload["algorithm"] == "ed25519"
        assert isinstance(payload["signature"], str)
        # Ed25519 signature is 64 bytes = 128 hex chars.
        assert len(payload["signature"]) == 128


def test_ctx_verify_passes_with_correct_key(tmp_path: Path) -> None:
    pack = _build_pack(tmp_path)
    priv, pub = _gen_keys(tmp_path)

    sign = runner.invoke(app, ["sign", str(pack), "--key", str(priv)])
    assert sign.exit_code == 0, sign.output

    verify = runner.invoke(app, ["verify", str(pack), "--key", str(pub)])
    assert verify.exit_code == 0, verify.output
    assert "Signature and integrity verified" in verify.output


def test_ctx_verify_fails_with_wrong_key(tmp_path: Path) -> None:
    pack = _build_pack(tmp_path)
    priv, _ = _gen_keys(tmp_path, name="signer")
    _, other_pub = _gen_keys(tmp_path, name="other")

    sign = runner.invoke(app, ["sign", str(pack), "--key", str(priv)])
    assert sign.exit_code == 0, sign.output

    verify = runner.invoke(app, ["verify", str(pack), "--key", str(other_pub)])
    assert verify.exit_code != 0
    assert "Verification failed" in verify.output
    assert "signature verification failed" in verify.output.lower()


def test_ctx_verify_fails_when_manifest_tampered(tmp_path: Path) -> None:
    pack = _build_pack(tmp_path)
    priv, pub = _gen_keys(tmp_path)

    sign = runner.invoke(app, ["sign", str(pack), "--key", str(priv)])
    assert sign.exit_code == 0, sign.output

    # Rewrite the pack with a mutated manifest while leaving the
    # signature.json intact, simulating post-signature tampering.
    tampered = tmp_path / "tampered.ctxpack"
    with zipfile.ZipFile(pack) as src, zipfile.ZipFile(tampered, "w", zipfile.ZIP_DEFLATED) as dst:
        for member in src.namelist():
            data = src.read(member)
            if member == MANIFEST:
                # Flip a byte in the JSON without breaking parseability:
                # swap "schema_version" so it remains valid JSON but
                # produces a different signed payload.
                data = data.replace(b'"schema_version"', b'"schema_version_x"', 1)
            dst.writestr(member, data)

    # Sanity: tampered manifest still parses as JSON.
    with zipfile.ZipFile(tampered) as archive:
        json.loads(archive.read(MANIFEST))
        assert SIGNATURE_JSON in archive.namelist()

    verify = runner.invoke(app, ["verify", str(tampered), "--key", str(pub)])
    assert verify.exit_code != 0
    assert "failed" in verify.output.lower()


def test_ctx_verify_fails_on_unsigned_pack(tmp_path: Path) -> None:
    pack = _build_pack(tmp_path)
    _, pub = _gen_keys(tmp_path)

    verify = runner.invoke(app, ["verify", str(pack), "--key", str(pub)])
    assert verify.exit_code != 0
    assert "not signed" in verify.output.lower()


def test_ctx_build_sign_produces_signed_pack(tmp_path: Path) -> None:
    """``ctx build --sign`` is the documented one-shot path; verify it."""
    priv, pub = _gen_keys(tmp_path)
    pack = tmp_path / "signed.ctxpack"

    build = runner.invoke(
        app,
        [
            "build",
            str(FIXTURES),
            "--to",
            str(pack),
            "--force",
            "--sign",
            str(priv),
        ],
    )
    assert build.exit_code == 0, build.output

    with zipfile.ZipFile(pack) as archive:
        assert SIGNATURE_JSON in archive.namelist()

    verify = runner.invoke(app, ["verify", str(pack), "--key", str(pub)])
    assert verify.exit_code == 0, verify.output
