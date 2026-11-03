# Elder: removal of two obsolete closed build caches,03.11.2026

Host user@10.245.1.11. The original receipt was read over the authorized SSH
connection from /home/user/timelearner-refactor/readbacks/storage-cleanup-20261103-closed-threshold-builds/receipt.json.

Only build-initial-threshold-normal-a1 and build-initial-threshold-normal-a3
were removed. Resolved absolute paths, CMake cache identity, absence of live
process references (arguments/mappings/executable/cwd), and absence of other
build-cache references were checked before deletion. Available bytes increased
from32971423744 to34327076864 (about1.26GiB). Background writes may affect the
exact observed delta.

Source Git stores and borrowed objects, all primary/results/model data,
A4 build and A5 runtime were retained. This is storage maintenance under the
user's permission to remove obsolete builds; no numerical validation or
scientific result is claimed. It does not resolve the separate GitHub DNS fault.
