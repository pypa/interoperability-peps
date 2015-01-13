#!/usr/bin/env python

from tuf.repository_tool import *

import datetime

repository = create_new_repository("repository")

repository.root.threshold = 2

# The root keys loaded to satisfy root's threshold.
donald_root_key = import_ed25519_privatekey_from_file("keystore/donald_root", password='pw')
richard_root_key = import_ed25519_privatekey_from_file("keystore/richard_root", password='pw')

# Any of these four root keys may be used to satisfy root's threshold.
repository.root.add_verification_key(import_ed25519_publickey_from_file("keystore/donald_root.pub"))
repository.root.add_verification_key(import_ed25519_publickey_from_file("keystore/richard_root.pub"))
repository.root.add_verification_key(import_ed25519_publickey_from_file("keystore/nick_root.pub"))
repository.root.add_verification_key(import_ed25519_publickey_from_file("keystore/noah_root.pub"))

repository.root.load_signing_key(donald_root_key)
repository.root.load_signing_key(richard_root_key)

# Add the public keys for the remaining top-level roles.
repository.targets.add_verification_key(import_ed25519_publickey_from_file("keystore/targets.pub"))
repository.snapshot.add_verification_key(import_ed25519_publickey_from_file("keystore/snapshot.pub"))
repository.timestamp.add_verification_key(import_ed25519_publickey_from_file("keystore/timestamp.pub"))

repository.targets.load_signing_key(import_ed25519_privatekey_from_file("keystore/targets", password='pw'))
repository.snapshot.load_signing_key(import_ed25519_privatekey_from_file("keystore/snapshot", password='pw'))
repository.timestamp.load_signing_key(import_ed25519_privatekey_from_file("keystore/timestamp", password='pw'))

# Create the delegated roles for the PEP 458 security model.  That is, the
# 'pypi-signed' role and its delegated bins.  Target files are evenly
# distributed to these bins.
pypi_signed_pub = import_ed25519_publickey_from_file("keystore/pypi-signed.pub")
pypi_signed_key = import_ed25519_privatekey_from_file("keystore/pypi-signed", password='pw')
repository.targets.delegate("pypi-signed", [pypi_signed_pub], [], restricted_paths=["repository/targets/packages/"])
repository.targets("pypi-signed").load_signing_key(pypi_signed_key)

# Create the bins for the 'pypi-signed' role.
targets = repository.get_filepaths_in_directory('repository/targets/packages', recursive_walk=True)
repository.targets('pypi-signed').delegate_hashed_bins(targets, [pypi_signed_pub], 16)

for delegation in repository.targets('pypi-signed').delegations:
  delegation.load_signing_key(pypi_signed_key)

# Set an expiration far into the future so the timestamp role so we can
# use this repository without having to worry about timestamp expiring.
repository.timestamp.expiration = datetime.datetime(2044, 10, 28, 12, 8)

# Write all the metadata to disk, signing metadata according to the private
# keys loaded for each role.
repository.write()
