# tdir issues and remediation plan

## Issues

1. **Process-wide working-directory race.** `tdir(chdir=True)` changes the
   process-wide current working directory. Overlapping contexts in different
   threads can restore the wrong directory or run code in another context's
   directory.
2. **Fill paths can escape the requested root.** A mapping key such as
   `../outside` or an absolute path is joined directly to the root and can
   write outside the temporary directory.
3. **Text encoding is implicit.** Text fixtures use the platform default for
   `Path.write_text()` and `read_text()`, so fixture bytes may vary by locale.
4. **Public fixture typing is too general.** `Arg` accepts `Any` inside a
   dictionary despite `fill()` accepting only a small recursive value set, and
   it omits bytes, bytearray, lists, and tuples that are supported at runtime.
5. **Published examples are invalid or misleading.** The examples use `=` in
   assertions, name `unittest.TestCase` as `TestCast`, and contain spelling
   mistakes, so copying them fails.

## Remediation plan

1. Decide and document the concurrency contract for `chdir=True`, then add a
   regression test for overlapping threads and implement the agreed behavior.
2. Decide whether path traversal and absolute mapping keys should be rejected,
   then validate every recursive key before creating or copying a file and add
   rejection tests.
3. Add opt-in or documented UTF-8 fixture encoding without changing existing
   callers' default text behavior; test Unicode text explicitly.
4. Model recursive fixture data accurately with explicit public type hints and
   test every supported value category.
5. Correct the README and generated API examples, and add documentation for
   the resolved concurrency and path-boundary rules.
