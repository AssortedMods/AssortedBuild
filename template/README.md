# __MOD_NAME__

__MOD_DESCRIPTION__

For Minecraft __MC__ on NeoForge and Fabric. Requires [Assorted Lib](https://github.com/AssortedMods/AssortedLib).
Branches are per Minecraft version and `__MC__` is the current one.

## Issue Reporting

Please include the following

* Minecraft version
* NeoForge version, or Fabric Loader and Fabric API versions
* __MOD_NAME__ version
* Assorted Lib version
* The full `latest.log`, and the crash report if the game crashed

## Building

You need JDK 25. The shared code is in `common` and both loaders build it in. The build setup comes
from [AssortedBuild](https://github.com/AssortedMods/AssortedBuild) and `assortedbuild_version` in
`gradle.properties` picks the version.

To build against a local copy of Assorted Lib, publish it first.

```bash
cd ../AssortedLib && ./gradlew publishToMavenLocal
```

Some useful commands

```bash
./gradlew build                        # build the mod
./gradlew :neoforge:runClient          # run it on NeoForge
./gradlew :fabric:runClient            # run it on Fabric
./gradlew :neoforge:runGameTestServer  # gametests on NeoForge
./gradlew :fabric:runGameTest          # gametests on Fabric
./gradlew :neoforge:runClientData      # datagen
./gradlew :neoforge:runServerData
```

## License

[LGPL-3.0-only](LICENSE).
