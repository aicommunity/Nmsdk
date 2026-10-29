# Rdk UTF-8 BOM normal gate: Elder-1

Native root 796a73075b930d634c905355541e47187aed6f5f, Rdk abc21b650471ef6d2e5ef9ba94429d34f3697323 (Core 8ebf64dd). Four CTest groups passed, including Test_MatrixNodeTextFormat, property/lifecycle/container checks. Both XmlTextEncoding tests additionally passed with individual GoogleTest XML: BOM/declaration combinations preserve numeric tags and Unicode text; BOM does not manufacture missing root/content. Normal Release, RDK_UNICODE_RUN=OFF; this does not claim a wide-platform runtime check.

The new runtime was configured only after the previous native owner gate finished; that earlier runtime was not modified. Runtime binary/INI hashes were verified before publication. Complete logs, XML and source/runtime manifest are retained with stored and raw hashes. Native adapter readback of four files/eleven values remains the separate M40 ASan evidence in s09-config-m40. No scientific selectivity verdict.
