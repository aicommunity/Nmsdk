# Function for obtaining version information from Git
# Format: {TAG} ({BRANCH}:{SHORT_HASH})
# Example: 1.2.1.0 (develop:b4ff447)

function(get_git_version OUTPUT_VAR)
    set(GIT_TAG "0.0.0.0")
    set(GIT_BRANCH "unknown")
    set(GIT_SHORT_HASH "unknown")

    # Ensure we are inside a Git repository
    find_package(Git QUIET)
    if(NOT Git_FOUND)
        message(STATUS "Git not found, using default version")
        set(${OUTPUT_VAR} "${GIT_TAG} (${GIT_BRANCH}:${GIT_SHORT_HASH})" PARENT_SCOPE)
        return()
    endif()

    # Get the latest tag
    execute_process(
        COMMAND ${GIT_EXECUTABLE} describe --tags --abbrev=0
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        OUTPUT_VARIABLE GIT_TAG_OUTPUT
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE GIT_TAG_RESULT
    )

    if(GIT_TAG_RESULT EQUAL 0 AND GIT_TAG_OUTPUT)
        string(STRIP "${GIT_TAG_OUTPUT}" GIT_TAG)
    endif()

    # Get the current branch name
    execute_process(
        COMMAND ${GIT_EXECUTABLE} rev-parse --abbrev-ref HEAD
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        OUTPUT_VARIABLE GIT_BRANCH_OUTPUT
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE GIT_BRANCH_RESULT
    )

    if(GIT_BRANCH_RESULT EQUAL 0 AND GIT_BRANCH_OUTPUT)
        string(STRIP "${GIT_BRANCH_OUTPUT}" GIT_BRANCH)
    endif()

    # Get short commit hash
    execute_process(
        COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        OUTPUT_VARIABLE GIT_HASH_OUTPUT
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE GIT_HASH_RESULT
    )

    if(GIT_HASH_RESULT EQUAL 0 AND GIT_HASH_OUTPUT)
        string(STRIP "${GIT_HASH_OUTPUT}" GIT_SHORT_HASH)
    endif()

    # Build the version string
    set(VERSION_STRING "${GIT_TAG} (${GIT_BRANCH}:${GIT_SHORT_HASH})")
    set(${OUTPUT_VAR} "${VERSION_STRING}" PARENT_SCOPE)

    message(STATUS "Git version: ${VERSION_STRING}")
endfunction()

