package com.grim3212.assorted.__MOD_PKG__.gametest;

import net.minecraft.gametest.framework.GameTestHelper;

import java.util.function.BiConsumer;
import java.util.function.Consumer;

import static com.grim3212.assorted.__MOD_PKG__.gametest.__MOD_CLASS__TestSupport.*;

/**
 * That the mod loads at all on a dedicated server, with its test mod beside it. Replace with real
 * feature tests as there is something to test.
 */
final class SmokeTests {

    private SmokeTests() {
    }

    static void register(BiConsumer<String, Consumer<GameTestHelper>> out) {
        out.accept("mod_loads", SmokeTests::modLoads);
    }

    private static void modLoads(GameTestHelper helper) {
        helper.assertTrue(helper.getLevel().getBlockState(CENTRE).isAir(), "the test box is not empty");
        helper.succeed();
    }
}
