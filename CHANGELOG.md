# Changelog

## 26.2.4

- Everything moved to the AssortedMods GitHub organization. Workflows, Renovate presets, the
  `fleet` repo list, the template and the maven publish now point at `AssortedMods/...` instead of
  `grim3212/...`.

## 26.2.3

- Fabric has no datagen of its own any more. The `datagenClient` run is gone and the datagen check
  in CI only runs the NeoForge datagen, which writes common's tree for both loaders.
- The release summary no longer fails the job on a mod that only has one of Modrinth or CurseForge.

## 26.2.2

- Publishing named its artifacts after the Gradle project - `common`, `fabric`, `neoforge` - rather
  than after `base.archivesName`, because the publication read the name while this plugin was being
  applied and the module plugins set it afterwards. Nothing resolves those ids, so a
  `publishToMavenLocal` silently left every consumer on the last good jar, and a release would have
  published a library no mod could find. The id is taken after evaluation now.

## 26.2.1

- The maven is a static site now - GitHub Pages serving grim3212/maven - and publishing is a
  publish into a checkout of it plus a push, with `ASSORTED_MAVEN` naming the checkout. The
  Reposilite, its deploy token and `MAVEN_DEPLOY_TOKEN` are gone; `MAVEN_DEPLOY_KEY` (a deploy key
  of the maven repository) replaces them in the workflows.
- `fleet new` no longer fails where no AssortedLib checkout sits beside the repository: it asks the
  maven for the newest one, and `--lib` overrides either.
- The CI runner's "Permission denied" on `gradlew`, and the helper class that a bare `build` in
  .gitignore had kept out of the repository.

## 26.2.0

First release, for the Minecraft 26.2 line.

- The build every Assorted mod used to carry - some 700 lines of Gradle and 300 of workflow per
  repository, identical but for a mod id and a JEI flag - lives here as convention plugins, a
  version catalog and one reusable workflow.
- Loom is pinned to `1.17.20`, the build `1.17-SNAPSHOT` was resolving to when this was made.
- `fleet` and `mods.yaml`: the mods as one thing.
- `template/`: a new mod in one command.
