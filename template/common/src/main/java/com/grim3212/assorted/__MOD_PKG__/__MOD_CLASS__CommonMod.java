package com.grim3212.assorted.__MOD_PKG__;

/**
 * Loader-agnostic startup. Both loader entry points call {@link #init()} and nothing else; anything
 * a loader needs beyond it goes through AssortedLib's {@code Services}.
 */
public class __MOD_CLASS__CommonMod {

    public static void init() {
        Constants.LOG.info(Constants.MOD_NAME + " starting up...");

        // Registries go here, in the order they depend on each other: blocks, then items, ...
    }
}
