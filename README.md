# Assorted Build

The shared build for every Assorted mod. Each mod only sets things like its id, name, version and which
Assorted Lib it needs. Everything else lives here, like the Minecraft and loader versions, the runs, the
tests and how releases go out. Change something here, bump one number in a mod, and the mod picks it up.

| Path | What it is |
| --- | --- |
| `gradle/libs.versions.toml` | Every shared version. Edit this for a Minecraft, loader or tooling update. |
| `plugin/` | The Gradle plugins every mod applies. |
| `catalog/` | Publishes the versions file so mods can use it. |
| `.github/workflows/mod-build.yml` | The build, test and release workflow every mod calls. |
| `fleet/` | The `fleet` command for doing something to every mod at once, and `repos.yaml` with the list of repos. |
| `template/` | What `fleet new` copies to make a new mod. |
| `renovate/` | Shared Renovate settings. |

## Using it from a mod

`settings.gradle` applies one plugin and each module's `build.gradle` applies its own.

```groovy
// settings.gradle
plugins {
    id 'com.grim3212.assorted' version "${assortedbuild_version}"
}
// build.gradle              -> id 'com.grim3212.assorted.root'
// common/build.gradle       -> id 'com.grim3212.assorted.common'
// fabric/build.gradle       -> id 'com.grim3212.assorted.fabric'
// neoforge/build.gradle     -> id 'com.grim3212.assorted.neoforge'
```

Everything a mod sets goes in its `gradle.properties`.

| Property | What it does |
| --- | --- |
| `assortedbuild_version` | Which version of this repo to build with. The first two numbers are the Minecraft version. |
| `version`, `group`, `license`, `issue_tracker` | The mod's own details. |
| `mod_id`, `mod_name`, `mod_author`, `mod_description` | Filled into `fabric.mod.json`, `neoforge.mods.toml` and `pack.mcmeta`. |
| `assortedlib_version` | The lowest Assorted Lib version the mod works with. |
| `jei_enabled` | Builds against JEI and adds it to the dev runs. |
| `client_gametests_enabled` | Adds the Fabric client gametests. Leave it off unless the mod has some. |
| `neoforge_ats_enabled` | Uses the mod's NeoForge access transformer. |
| `common_runs_enabled` | Adds client and server runs to the common module. Rarely needed. |
| `modrinth_id`, `curseforge_id`, `curseforge_slug`, `release_type` | Where a release gets uploaded. A blank id skips that site. |

If a mod needs something extra it can add normal Gradle code to its own `build.gradle`. AssortedStorage
does this for Curios.

### Several mods in one repo

A repo can hold a group of mods, like AssortedUtil does. Each mod is a folder under `mods` and the root
`gradle.properties` lists them.

```properties
family_name=Assorted Util
assorted_mods=graves,doubledoors,itemreplacer,time,lightoverlay,damagenumbers
```

Each folder is set up like a normal mod with its own `gradle.properties`, `README.md`, `CHANGELOG.md`
and `common`, `fabric` and `neoforge` folders. Anything that belongs to a single mod, like its id or
version, has to go in that mod's own `gradle.properties`. Commands use the folder name, so
`./gradlew :graves:publishMods` releases just that mod.

`family_id`, `family_icons` and `family_manual_order` in the root `gradle.properties` are shared by every
mod in the group. The build turns them into a `Family` class in each mod, so they only ever get written
once.

Adding `bundled_mods=icepixie,treasuremob` to a mod makes it a bundle. Its jar includes those other
mods, the same way Fabric API includes its modules. AssortedMobs uses this so Assorted Mobs can still
be one download while each mob is also its own mod.

A group that used to be one released mod sets `family_split_version` in the root `gradle.properties`
to the bundle's first version after the split, like `family_split_version=10.0.0`. Every mod in the
group then refuses to load next to that old mod from before the split, on both loaders. The bundle
keeps the old mod's id, so it is left out.

To play with every mod in the repo at once, run `./gradlew :all:neoforge:runClient` or
`:all:fabric:runClient`. Those runs save to `run/all-neoforge` and `run/all-fabric`.

To test local changes to this repo or Assorted Lib, run `./gradlew publishToMavenLocal` in it first.

## Releasing this repo

1. Make your changes to `gradle/libs.versions.toml` or the plugins
2. Bump `version` in `gradle.properties`. A new Minecraft version starts a new number line.
3. Run the Build workflow with `publish` ticked
4. Run `fleet/fleet bump-build` to move every mod to the new version

## The maven

`maven.grimoid.com` is GitHub Pages serving the [AssortedMods/maven](https://github.com/AssortedMods/maven)
repo. A publish checks that repo out, publishes into its `mods` folder and pushes one commit. The push
uses the `MAVEN_DEPLOY_KEY` secret. Pages can take up to ten minutes to show a new release.

To publish by hand, check the maven out next to this repo, run
`ASSORTED_MAVEN=../maven/mods ./gradlew publishAllPublicationsToAssortedModsRepository`, then commit and push it.

The Build workflow also makes a new mod from `template/` and builds it, so a change that breaks mods
fails here first.

## The fleet

```
fleet/fleet status                     which mods are on what and which have changes
fleet/fleet exec git pull              run a command in every repo
fleet/fleet bump-build                 set assortedbuild_version everywhere
fleet/fleet pr <branch> "<message>"    open a PR in every repo with changes
fleet/fleet release all                dry run release everywhere (--real to upload)
fleet/fleet release assortedgraves     release one mod from a group on its own
fleet/fleet new "Assorted Foo" foo "…" make a new mod
```

`pr` and `release` need the [GitHub CLI](https://cli.github.com). The repos are expected next to this one.
Set `FLEET_ROOT` if they are somewhere else. `repos.yaml` only lists the repos. Each mod's ids come
from its own `gradle.properties`.

## Layout of a mod

The shared code goes in `common` and both loaders build it in. The NeoForge datagen writes the generated
files for both loaders into `common/src/generated`. Gametests go in a `gametest` source set and never
end up in a jar.

## License

[LGPL-3.0-only](LICENSE).
