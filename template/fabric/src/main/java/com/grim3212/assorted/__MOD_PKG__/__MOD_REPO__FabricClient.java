package com.grim3212.assorted.__MOD_PKG__;

import com.grim3212.assorted.__MOD_PKG__.client.__MOD_CLASS__Client;
import net.fabricmc.api.ClientModInitializer;

public class __MOD_REPO__FabricClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        __MOD_CLASS__Client.init();
    }
}
