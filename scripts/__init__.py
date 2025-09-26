"""Top-level package marker for the repository's automation scripts.

This file exists so that Python treats the `scripts` directory as a package.
Doing so allows companion tooling (for example, the autopilot orchestrator)
to import helper modules such as `scripts.automation.cursor_dispatch` without
resorting to brittle `sys.path` manipulations. Keeping the package explicit
also reinforces the repository's documentation rule to include detailed
explainers alongside automation source files.

No runtime logic lives here by design—future maintainers can extend the
package by adding shared helpers in sibling modules while retaining this file
as lightweight context.
"""


