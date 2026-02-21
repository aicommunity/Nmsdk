# x64-windows with VS2019 (v142) toolset for CRT compatibility with Qt 5.15.2 msvc2019_64.
# Use this triplet with win-vs2019-*-localqt so that vcpkg-built deps (boost, curl, etc.)
# use the same CRT as the app and Qt (v142); avoids mixing v143 (VS2022) and v142 (VS2019).
set(VCPKG_TARGET_ARCHITECTURE x64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_LIBRARY_LINKAGE dynamic)
set(VCPKG_PLATFORM_TOOLSET v142)
