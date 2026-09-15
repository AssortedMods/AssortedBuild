package com.grim3212.assorted.__MOD_PKG__.gametest;

import net.minecraft.gametest.framework.GameTestHelper;

import java.util.function.BiConsumer;
import java.util.function.Consumer;

/**
 * Automated in-world checks for __MOD_NAME__. The tests live in small {@code <Feature>Tests}
 * classes; this only lists them. Each name here needs a matching
 * {@code data/__MOD_ID__/test_instance/<name>.json}.
 */
public final class __MOD_CLASS__GameTests {

    private __MOD_CLASS__GameTests() {
    }

    /** Every test in this mod, named once, so both loaders register the same set. */
    public static void forEach(BiConsumer<String, Consumer<GameTestHelper>> out) {
        SmokeTests.register(out);
    }
}
