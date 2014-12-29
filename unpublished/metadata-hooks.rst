PEP: XXX
Title: Metadata Hooks for Python Software Packages
Version: $Revision$
Last-Modified: $Date$
Author: Nick Coghlan <ncoghlan@gmail.com>
BDFL-Delegate: Nick Coghlan <ncoghlan@gmail.com>
Discussions-To: Distutils SIG <distutils-sig@python.org>
Status: Draft
Type: Standards Track
Content-Type: text/x-rst
Requires: 426
Created: 3 Mar 2014


Abstract
========

This PEP describes ``python.metadata_hooks``, an extension to the Python
distribution metadata that allows installed software to execute potentially
privileged code when other software is installed or removed.

Like all metadata extensions, this extension is independently versioned.
Changing any of the formats requires replacement of this PEP, but does not
require an update to the core packaging metadata.


The ``python.metadata_hooks`` extension
=======================================

The ``python.metadata_hooks`` extension is used to define operations to be
invoked on the distribution in the following situations:

* a relevant distribution has been installed or changed on the system
* a relevant distribution has been completely uninstalled from the system

The following subfields determine when hooks are triggered:

* ``export_groups``: trigger based on named export groups
* ``extensions``: trigger based on named extensions

Note that distributions *do* trigger their own install hooks, but do
*not* trigger their own uninstall hooks.

This extension is currently at version ``1.0``, and thus the
``extension_metadata`` field may be omitted without losing access to any
functionality.

Depending on the specific use case for the hooks, projects may choose to
set the ``required_extension`` field to ``true``.


Hook signatures
---------------

The currently defined metadata hooks are:

* ``postinstall``: run after a relevant distribution has been installed,
  upgraded or downgraded on the current system. May also be run as part
  of a system state resync operation. If the hook is not defined, it
  indicates no distribution specific actions are needed following
  installation.
* ``postuninstall``: run after a relevant distribution has been completely
  removed from the current system. If the hook is not defined, it indicates
  no distribution specific actions are needed following uninstallation.

The required signatures of these hooks are as follows::

    def postinstall(current_meta, previous_meta=None):
        """Run following installation or upgrade of a relevant distribution

        *current_meta* is the distribution metadata for the version now
        installed on the current system
        *previous_meta* is either omitted or ``None`` (indicating a fresh
        install) or else the distribution metadata for the version that
        was previously installed (indicating an upgrade, downgrade or
        resynchronisation of the system state).
        """

    def postuninstall(previous_meta):
        """Run after complete uninstallation of a relevant distribution

        *previous_meta* is the distribution metadata for the version that
        was previously installed on the current system
        """

Export group hooks
------------------

Export group hooks are named after the export group of interest::

    "export_groups": {
      "ComfyChair.plugins": {
        "postinstall": "ComfyChair.plugins:install_hook",
        "postuininstall": "ComfyChair.plugins:uninstall_hook"
      }
    }

The nominated hooks will then be invoked appropriately for any distribution
that publishes that export group as part of their ``python.exports``
extension metadata.

A trailing ".*" may be used to request prefix matching rather than
requiring an exact match on the export group name.


Extension hooks
---------------

Extension hooks are named after the metadata extension of interest::

    "extensions": {
      "python.exports": {
        "postinstall": "pip.export_group_hooks:run_install_hooks",
        "postuininstall": "pip.export_group_hooks:run_uninstall_hooks"
      }
      "python.commands": {
        "postinstall": "pip.command_hook:install_wrapper_scripts",
      }
    }

(Note: this is just an example, but the intent is that pip *could* implement
that functionality that way if it wanted to).

A trailing ".*" may be used to request prefix matching rather than
requiring an exact match on the extension name.


Guidelines for metadata hook invocation
---------------------------------------

.. note::

   Metadata hooks are likely to run with elevated privileges, this needs
   to be considered carefully (e.g. by *requiring* that metadata hook
   installation be opt in when using the standard tools and running with
   elevated privileges).

The given parameter names are considered part of the hook signature.
Installation tools MUST call metadata hooks solely with keyword arguments.

When metadata hooks are defined, it is assumed that they MUST be executed
to obtain a properly working installation of the distribution, and to
properly remove the distribution from a system.

Installation tools MUST ensure the new or updated distribution is fully
installed, and available through the import system and installation database
when invoking install hooks.

Installation tools MUST ensure the removed distribution is fully uninstalled,
and no longer available through the import system and installation database
when invoking uninstall hooks.

Installation tools MUST call metadata hooks with full metadata (including
all extensions), rather than only the core metadata.

Installation tools SHOULD invoke metadata hooks automatically after
installing a distribution from a binary archive.

When installing from an sdist, source archive or VCS checkout, installation
tools SHOULD create a binary archive using ``setup.py bdist_wheel`` and
then install the binary archive normally (including invocation of any
metadata hooks). Installation tools SHOULD NOT invoke ``setup.py install``
directly.

Installation tools SHOULD treat an exception thrown by a metadata install
hook as a failure of the installation and revert any other changes made
to the system. The installed distribution responsible for the hook that
failed should be clearly indicated to the user.

Installation tools SHOULD provide a warning to the user for any exception
thrown by a metadata uninstall hook, again clearly indicating to the user
the installed distribution that triggered the warning.

Installation tools MUST NOT silently ignore metadata hooks, as failing
to call these hooks may result in a misconfigured installation that fails
unexpectedly at runtime. Installation tools MAY refuse to install
distributions that define metadata hooks, or require that users
explicitly opt in to permitting the installation of packages that
define such hooks.


Guidelines for metadata hook implementations
--------------------------------------------

The given parameter names are considered part of the hook signature.
Metadata hook implementations MUST use the given parameter names.

Metadata hooks SHOULD NOT be used to provide functionality that is
expected to be provided by installation tools (such as rewriting of
shebang lines and generation of executable wrappers for Windows).

Metadata hook implementations MUST NOT make any assumptions regarding the
current working directory when they are invoked, and MUST NOT make
persistent alterations to the working directory or any other process global
state (other than potentially importing additional modules, or other
expected side effects of running the distribution).

Metadata install hooks have access to the full metadata for the release being
installed, that of the previous/next release (as appropriate), as well as
to all the normal runtime information (such as available imports). Hook
implementations can use this information to perform additional platform
specific installation steps. To check for the presence or absence of
"extras", hook implementations should use the same runtime checks that
would be used during normal operation (such as checking for the availability
of the relevant dependencies).


Open Questions
==============

* Do we want preinstall and preuninstall hooks? If yes, can the hook
  indicate that the installation/uninstallation should be handled by a
  different utility (this would allow apt-get/yum/etc to hook into system
  Python installations, ensuring that the system Python remains
  consistent, but allowing users to use the familiar cross-platform Python
  commands and namespace.
* How do we deal with the --user installation scheme?


Copyright
=========

This document has been placed in the public domain.


..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
