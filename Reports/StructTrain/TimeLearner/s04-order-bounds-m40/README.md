# Native Rdk component-order bounds: m40

The actual production UContainer method is linked by the maintained Test_UContainer_Components target. No function body was copied into a synthetic test.

On M40, test-only Rdk e2bcd8da5bab016bd3fd703c42e519e56b633081 reproduces a wrong-order assertion for INT_MAX relative step and an AddressSanitizer heap-buffer-overflow for moving a child to the vector end. The first preparation attempt omitted BUILD_TESTING and built no test; it is retained separately. Corrected preparation explicitly enables BUILD_TESTING.

Rdk 2cfda44d738f6291914217dba9cd223acae35bfd uses a wide destination, saturates absolute positions before subtraction, and stops forward shifting before the destination. All 13 native cases pass on Elder-1 normally and M40 under ASan (detect_leaks=0). The three new cases check the actual objects/IDs/cache order, maximum relative step, and minimum absolute position/invalid source indices.

This is addressed unit evidence, not the whole lifecycle/physics matrix or a scientific recognition result. Native import/frozen integration and full maintained suites are tracked separately. No causal claim about historical August experiments follows from this finding.

Git is the sole transfer mechanism. Stored gzip bytes and uncompressed payloads have independent SHA256 entries. Executables and credentials are not committed.
