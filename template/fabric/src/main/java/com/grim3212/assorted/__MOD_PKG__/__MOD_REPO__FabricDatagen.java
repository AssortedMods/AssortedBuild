package com.grim3212.assorted.__MOD_PKG__;

import net.fabricmc.fabric.api.datagen.v1.DataGeneratorEntrypoint;
import net.fabricmc.fabric.api.datagen.v1.FabricDataGenerator;

/**
 * Fabric's half of datagen: the recipes, tags and loot that carry Fabric's own load conditions.
 * Models and language come from the NeoForge datagen, which writes into common for both loaders.
 */
public class __MOD_REPO__FabricDatagen implements DataGeneratorEntrypoint {

    @Override
    public void onInitializeDataGenerator(FabricDataGenerator fabricDataGenerator) {
        FabricDataGenerator.Pack pack = fabricDataGenerator.createPack();

        // pack.addProvider((output, registriesFuture) -> new FabricConditionalRecipeProvider(output, registriesFuture, new __MOD_CLASS__Recipes.Runner(output, registriesFuture)));
    }
}
