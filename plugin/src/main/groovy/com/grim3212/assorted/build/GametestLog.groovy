package com.grim3212.assorted.build

import org.gradle.api.GradleException
import org.gradle.api.Project
import org.gradle.api.Task

import java.util.regex.Pattern

/**
 * Fails a gametest run that logged an error naming our mods, as Minecraft drops data it cannot read and the tests pass
 * without it. Build-side, so none of it ships; a mod excuses an expected error with a regex in {@code gametest_log_allow}.
 */
final class GametestLog {

    /** An error or fatal line, in either loader's layout; any other line opening with a timestamp ends it. */
    private static final Pattern ERROR = Pattern.compile('^\\[[^\\]]+\\] \\[[^\\]]+/(ERROR|FATAL)\\]')
    private static final Pattern NEXT_LINE = Pattern.compile('^\\[\\d')
    private static final Pattern COLOR = Pattern.compile('\u001B\\[[0-9;]*m')

    private GametestLog() {
    }

    /** Checks the run's {@code logs/latest.log} once {@code task} succeeds. */
    static void checkAfter(Project project, String taskName, File gameDirectory) {
        File log = new File(gameDirectory, 'logs/latest.log')
        String allow = project.findProperty('gametest_log_allow')?.toString()?.trim()
        project.tasks.matching { it.name == taskName }.configureEach { Task task ->
            // A log left by an earlier run must not pass or fail this one.
            task.doFirst { log.delete() }
            task.doLast { check(log, allow ? Pattern.compile(allow) : null) }
        }
    }

    static void check(File log, Pattern allow) {
        if (!log.isFile()) {
            throw new GradleException("The gametest run wrote no log at $log to check for errors")
        }

        List<List<String>> errors = []
        List<String> current = null
        log.eachLine('UTF-8') { String raw ->
            String line = COLOR.matcher(raw).replaceAll('')
            if (ERROR.matcher(line).find()) {
                current = [line]
                errors << current
            } else if (NEXT_LINE.matcher(line).find()) {
                current = null
            } else if (current != null) {
                current << line
            }
        }

        List<String> ours = errors.collect { it.join('\n') }
                .findAll { it.toLowerCase(Locale.ROOT).contains('assorted') }
                .findAll { allow == null || !allow.matcher(it).find() }
        if (!ours.isEmpty()) {
            String shown = ours.take(10).collect { it.readLines().take(6).join('\n    ') }.join('\n\n  ')
            throw new GradleException("The gametests passed, but ${ours.size()} error(s) naming our mods were logged in $log:\n\n  $shown")
        }
    }
}
