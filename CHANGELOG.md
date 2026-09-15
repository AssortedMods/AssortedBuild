# Changelog

## 26.2.0

First release, for the Minecraft 26.2 line.

- The build every Assorted mod used to carry - some 700 lines of Gradle and 300 of workflow per
  repository, identical but for a mod id and a JEI flag - lives here as convention plugins, a
  version catalog and one reusable workflow.
- Loom is pinned to `1.17.20`, the build `1.17-SNAPSHOT` was resolving to when this was made.
- `fleet` and `mods.yaml`: the mods as one thing.
- `template/`: a new mod in one command.
