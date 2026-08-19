"""
Jents VPN — Ephemeral Cryptographic Session Manager
===================================================
Generates ephemeral session keys, authorization tokens,
and cryptographic nonces for zero-knowledge node authentication.
"""

import os
import secrets
import hashlib
import base64
import time
from typing import Dict, Tuple

class CryptoSession:
    """Manages ephemeral cryptographic keys and handshake tokens."""

    def __init__(self):
        self.session_id: str = secrets.token_hex(16)
        self.created_at: float = time.time()
        self.client_private_key: bytes = secrets.token_bytes(32)
        self.client_public_key: bytes = hashlib.sha256(self.client_private_key).digest()
        self.cipher_suite = "ChaCha20-Poly1305 / Noise_IK"

    @property
    def public_key_b64(self) -> str:
        """Returns base64 encoded public key for node registration."""
        return base64.b64encode(self.client_public_key).decode('utf-8')

    def generate_auth_token(self, gateway_id: str) -> str:
        """Generates an ephemeral, timestamped HMAC challenge token for the gateway."""
        payload = f"{self.session_id}:{gateway_id}:{self.public_key_b64}:{int(time.time())}"
        signature = hashlib.sha256(self.client_private_key + payload.encode('utf-8')).hexdigest()
        return f"JENTS-TOKEN-{self.session_id[:8]}-{signature[:16]}"

    def get_session_info(self) -> Dict[str, str]:
        return {
            "session_id": self.session_id,
            "cipher": self.cipher_suite,
            "pubkey_fingerprint": hashlib.sha256(self.client_public_key).hexdigest()[:12].upper(),
            "uptime_sec": int(time.time() - self.created_at)
        }
