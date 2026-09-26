package com.grim3212.assorted.build

import org.gradle.api.Project
import org.gradle.api.artifacts.VersionCatalogsExtension

/**
 * What the convention plugins read from a mod: the on/off knobs in its gradle.properties and the
 * shared versions in the catalog. Kept to these two so the knob list stays visible in one place.
 */
final class Assorted {

    private Assorted() {
    }

    /** The version this plugin jar was built as; the catalog is imported at the same one. */
    static String buildVersion() {
        Properties properties = new Properties()
        Assorted.getResourceAsStream('/assortedbuild.properties').withCloseable { properties.load(it) }
        return properties.getProperty('version')
    }

    /** A boolean gradle.properties knob, absent meaning {@code fallback}. */
    static boolean flag(Project project, String name, boolean fallback = false) {
        Object value = project.findProperty(name)
        return value == null ? fallback : Boolean.parseBoolean(value.toString().trim())
    }

    /**
     * The mod directories of a family repo, from {@code assorted_mods} in the root gradle.properties.
     * Empty for a repo that is one mod.
     */
    static List<String> modDirs(String assortedMods) {
        return (assortedMods ?: '').split(',')*.trim().findAll { it }
    }

    /** A sibling module of {@code project} - its mod's {@code common}, say - in either repo layout. */
    static Project module(Project project, String name) {
        return project.parent.project(name)
    }

    /** A version from libs.versions.toml by its alias, e.g. {@code 'fabric-api'}. */
    static String catalogVersion(Project project, String alias) {
        return project.extensions.getByType(VersionCatalogsExtension).named('libs')
                .findVersion(alias)
                .orElseThrow { new IllegalStateException("libs.versions.toml has no version '$alias'") }
                .requiredVersion
    }
}
