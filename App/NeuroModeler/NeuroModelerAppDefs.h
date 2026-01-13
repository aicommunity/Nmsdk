#pragma once

#ifndef RDK_APP_VERSION
#define RDK_APP_VERSION "0.0.0.0 (unknown:unknown)"
#endif
#define RDK_APP_URL "https://neuromodeler.ru"
#define RDK_APP_LICENSE "There is a public domain software (2000-2026)"

// Suppress redefinition warnings for macros that may be defined via -D in command line
#ifdef __GNUC__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wbuiltin-macro-redefined"
#endif
#define RDK_APP_NAME "Neuro Modeler"
#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif


