# Maintained analyze CLI on original native data

Root 77bf00857829f3a7ca87b381b3285f53e7917250. Twenty domain-auditor/CLI tests pass. The actual production module entry point is also executed in fresh Python processes on twenty-seven real records/packages: five completed solo states, twenty diagnostic stopped states, one original probe with its CSV and one physical domain preview. All calls complete; scientific evaluation verdict stays null. Diagnostic/unresolved outcomes are preserved.

A separate Python-only Git worktree is used. No live native source/cache/runtime is changed and no native binary is rebuilt. Runtime and source-tree metadata are recorded. input-provenance.json links each primary input SHA256 to a published Git evidence commit and its raw-file manifest; all associated native primary traces remain in those original packages rather than being silently replaced.

Controls cover corrupt schema, missing required primary trace, non-overwriting output and explicit schema-1 adapter without physical confirmation. This is the native evidence subset of analyze, not the completed recognition scorer, general experiment runner or all stage-9 commands.
