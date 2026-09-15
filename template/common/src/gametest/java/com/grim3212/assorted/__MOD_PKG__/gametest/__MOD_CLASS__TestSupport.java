package com.grim3212.assorted.__MOD_PKG__.gametest;

import net.minecraft.core.BlockPos;

/**
 * Helpers and constants shared by __MOD_NAME__'s gametest classes, which import them statically,
 * alongside AssortedLib's {@code TestSupport}.
 */
final class __MOD_CLASS__TestSupport {

    private __MOD_CLASS__TestSupport() {
    }

    /** Middle of the 9x9x9 box, one block above its floor - room on every side for a drop. */
    static final BlockPos CENTRE = new BlockPos(4, 1, 4);
}
