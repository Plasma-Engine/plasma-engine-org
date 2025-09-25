# Repository inventory artifacts

This directory contains machine-generated listings of the workspace to support architecture and service inventory.

- `structure.ls.txt`: Recursive `ls -laR` of the workspace
- `structure.git.txt`: Git-tracked files with long listings
- `structure.find.txt`: Simple path list using `find`
- `structure.eza.txt`: Placeholder for `exa`/`eza` style listing

Notes:
- The requested command `exa -1 --classify --long --git --recurse .` could not be executed in this environment because `exa`/`eza` is not available. Use the provided artifacts as a functional equivalent. If needed, install `eza` and re-run to generate `structure.eza.txt`.

