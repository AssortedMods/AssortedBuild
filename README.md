# Assorted Build

How every Assorted mod is built, in one place. A mod repository says what the mod is - its id,
name, version, the AssortedLib it needs, a few on/off knobs - and this repository says everything
else: the Minecraft, NeoForge, Fabric and tooling versions, the module layout, the runs, the tests,
how a release goes out. Change it here, bump one number in a mod, and the mod has it.

What is in here:

| Path | What |
| --- | --- |
| `gradle/libs.versions.toml` | Every shared version. The one file to edit for a Minecraft, loader or tooling bump. |
| `plugin/` | The Gradle convention plugins (`com.grim3212.assorted`, `.root`, `.common`, `.fabric`, `.neoforge`). |
| `catalog/` | Publishes the TOML above as a version catalog the settings plugin imports. |
| `.github/workflows/mod-build.yml` | The reusable build/test/release pipeline every mod's workflow calls. |
| `fleet/` | `fleet`, the command for doing something to all the mods at once, and `mods.yaml`, the list of them. |
| `template/` | What `fleet new` stamps a new mod out of. |
| `renovate/` | Shared Renovate presets. |

## Using it from a mod

`settings.gradle` applies one plugin and each module's `build.gradle` applies its convention:

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

`gradle.properties` is the whole per-mod surface:

| Property | Meaning |
| --- | --- |
| `assortedbuild_version` | Which release of this repository to build with. The first two segments are the Minecraft version it targets. |
| `version`, `group`, `license`, `issue_tracker` | The mod's own. |
| `mod_id`, `mod_name`, `mod_author`, `mod_description` | Expanded into `fabric.mod.json`, `neoforge.mods.toml`, `pack.mcmeta` and the jar manifest. |
| `assortedlib_version` | The AssortedLib the mod **needs** - its minimum, declared as such on both loaders. Absent only in AssortedLib itself. |
| `jei_enabled` | Compile against the JEI API and put JEI on the dev runtime. |
| `client_gametests_enabled` | Add the Fabric client gametest run and its production-run task. Off unless the mod has client tests. |
| `neoforge_ats_enabled` | Apply `neoforge/src/main/resources/META-INF/accesstransformer.cfg`. |
| `common_runs_enabled` | Add client/server runs to the common module (rarely useful). |
| `modrinth_id`, `curseforge_id`, `curseforge_slug`, `release_type` | Where and how a release goes. A blank id publishes to nowhere. |

A mod that needs something more writes plain Gradle in its module's `build.gradle` on top of the
convention - AssortedStorage's optional Curios dependency, for example. The plugin does not grow a
knob for one mod.

Versions come from the catalog and are also exposed as the project properties they always were
(`minecraft_version`, `neoforge_version`, `fabric_version`, `jei_version`, ...), so a mod's own
script and its metadata templates keep working unchanged.

Local checkouts of AssortedBuild and AssortedLib are picked up from `mavenLocal()` after
`./gradlew publishToMavenLocal` in either one - the same step as before for an unreleased library.

## Releasing this repository

1. Edit `gradle/libs.versions.toml` and/or the plugins.
2. Bump `version` in `gradle.properties` (`26.2.x` for the current Minecraft line; a new Minecraft
   version starts a new line).
3. Run the Build workflow with `publish` ticked, or `./gradlew publish` with the maven credentials.
4. `fleet/fleet bump-build` moves every mod to it; `fleet/fleet status` shows who is behind.

The workflow's `template` job scaffolds a mod from `template/` and builds it against the freshly
built plugin, so a change that breaks a mod build fails here first.

## The fleet

```
fleet/fleet status                     who is on what, who is dirty
fleet/fleet exec git pull              anything, in every checkout
fleet/fleet bump-build                 assortedbuild_version everywhere
fleet/fleet pr <branch> "<message>"    one PR per dirty checkout
fleet/fleet release all                dispatch a dry-run release everywhere (--real to upload)
fleet/fleet new "Assorted Foo" foo "…" a new mod
```

`pr` and `release` need the [GitHub CLI](https://cli.github.com). Checkouts are expected beside
this repository; `FLEET_ROOT` points elsewhere.

## Layout of a mod

`common/` holds the loader-agnostic code and both loader modules compile those sources inline. The
NeoForge datagen writes models and language into `common/src/generated/client` and data into
`common/src/generated/server`; Fabric's own datagen writes into `fabric/src/generated/resources`.
Gametests live in a `gametest` source set in every module and never reach a jar.

## License

[LGPL-3.0-only](LICENSE).
