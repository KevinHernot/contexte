"""Cryptographic signing for context packs."""

from __future__ import annotations

from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


def generate_key_pair(output_dir: Path, name: str = "contexte") -> tuple[Path, Path]:
    """Generates an Ed25519 key pair for signing context packs."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    output_dir.mkdir(parents=True, exist_ok=True)
    priv_path = output_dir / f"{name}_private.pem"
    pub_path = output_dir / f"{name}_public.pem"

    with open(priv_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(pub_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
    return priv_path, pub_path


def sign_data(data: bytes, private_key_path: Path) -> str:
    """Signs data using an Ed25519 private key and returns hex signature."""
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise ValueError("Only Ed25519 keys are supported for context pack signing.")

    signature = private_key.sign(data)
    return signature.hex()


def verify_signature(data: bytes, signature_hex: str, public_key_path: Path) -> bool:
    """Verifies an Ed25519 signature against data."""
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    if not isinstance(public_key, ed25519.Ed25519PublicKey):
        raise ValueError("Only Ed25519 keys are supported for context pack verification.")

    try:
        public_key.verify(bytes.fromhex(signature_hex), data)
        return True
    except Exception:
        return False
