import os


# Configuration is created while app modules import, so tests set the secret before collection.
os.environ.setdefault("JWT_SECRET_KEY", "test-only-signing-key-that-is-at-least-32-chars")
