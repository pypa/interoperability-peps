"""
<Program Name>
  example_client.py

<Author>
  Vladimir Diaz <vladimir.v.diaz@gmail.com>

<Started>
  January 9, 2015.

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Example script demonstrating custom python code a software updater
  utilizing The Update Framework may write to securely update files.
  The 'basic_client.py' script can be used on the command-line to perform
  an update that will download and update all available targets; writing
  custom code is not required with 'basic_client.py'.
  
  The custom examples below demonstrate:
  (1) updating a specific target explicitly named and signed a "pypi-signed" bin.

  It assumes a server is listening on 'http://localhost:8001'.  One can be
  started by navigating to the 'examples/repository/' and starting:
  $ python -m SimpleHTTPServer 8001
"""

import logging

import tuf.client.updater

# Uncomment the line below to enable printing of debugging information.
tuf.log.set_log_level(logging.INFO)

# Set the local repository directory containing the metadata files.
tuf.conf.repository_directory = '.'

# Set the repository mirrors.  This dictionary is needed by the Updater
# class of updater.py.  The client will download metadata and target
# files from any one of these mirrors.
repository_mirrors = {'mirror1': {'url_prefix': 'http://localhost:8001',
                                  'metadata_path': 'metadata',
                                  'targets_path': 'targets',
                                  'confined_target_dirs': ['']}}

# Create the Upater object using the updater name 'tuf-example'
# and the repository mirrors defined above.
updater = tuf.client.updater.Updater('tuf-example', repository_mirrors)

# Set the local destination directory to save the target files.
destination_directory = './targets'

# Example demonstrating an update that downloads a specific target.
# The target is signed for by a 'pypi-signed' bin.
updater.refresh()
warehouse_target = updater.target('packages/warehouse/warehouse-14.2.1.tar.gz')
updated_target = updater.updated_targets([warehouse_target], destination_directory)

for target in updated_target:
  updater.download_target(target, destination_directory)
