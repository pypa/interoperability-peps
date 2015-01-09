#!/usr/bin/env python

from tuf.repository_tool import *

# Generate and write an Ed25519 key pair.  The private key is saved encrypted.
# A 'password' argument may be supplied, otherwise a prompt is presented.

# They keys for the root role.  For example, the root role may have a threshold
# of two, and can be signed by any of the four root keys.
generate_and_write_ed25519_keypair('keystore/donald_root', password='pw')
generate_and_write_ed25519_keypair('keystore/richard_root', password='pw')
generate_and_write_ed25519_keypair('keystore/nick_root', password='pw')
generate_and_write_ed25519_keypair('keystore/noah_root', password='pw')

# The keys for the non-root top-level roles and one delegated role
# (pypi-signed)
generate_and_write_ed25519_keypair('keystore/timestamp', password='pw')
generate_and_write_ed25519_keypair('keystore/snapshot', password='pw')
generate_and_write_ed25519_keypair('keystore/targets', password='pw')
generate_and_write_ed25519_keypair('keystore/pypi-signed', password='pw')
