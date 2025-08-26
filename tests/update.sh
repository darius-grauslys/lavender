#!/bin/bash

# this script will update the test_suite to include any
# newly added modules and directories.
# For each directory, there will be a corresponding header
# and source file of the name: test_suite_(DIRNAME)
# This header will have an include_test_suite__(DIRNAME)
# function that takes an MunitSuite pointer, and establishes
# the MunitSuite fields to correspond to the dirname test_suite.
#
# Each source file will have its own test_suite which is
# a sub_suite automatically added to the dirname test suite.
# If a test_suite source file for the original source file
# is generated, it will include a #warning to inform the
# source maintainer to write tests for their newly added module.
#
# For every bash function call to update(...) there should be
# a directory in ./tests/ with an ./include and ./source

export base_dir=$(realpath "${GAME_DIR}")
export core_dir=$(realpath "${LAVENDER_DIR}/core/source")
export platform_dir=$(realpath "${LAVENDER_DIR}/${PLATFORM}/source")

gen_main() {
    find $2 -iname test_suite_main.c -exec sed -i "s/#include <main.c>//" {} \;
    output="$2/main.c"
    printf "#include <MAIN_TEST_SUITE__CORE_ANCIENTS_GAME.h>

int main(int argc, char* argv[MUNIT_ARRAY_PARAM(argc + 1)]) {
    MunitSuite test_suite;

    include_test_suite__CORE_ANCIENTS_GAME(&test_suite);

    return munit_suite_main(&test_suite, (void*) \"µnit\", argc, argv);
}\n" > $output
    cp ${LAVENDER_DIR}/tests/templates/test_util.h "$1/test_util.h"
    cp ${LAVENDER_DIR}/tests/templates/munit.h "$1/munit.h"
  cp ${LAVENDER_DIR}/tests/templates/munit.c "$2/munit.c"
    if [ -n "$3" ]; then
        return
    fi
    if ! test -f "$1/platform_defines.h"; then
        cp ${LAVENDER_DIR}/tests/templates/include/platform_defines.h "$1/platform_defines.h"
    fi
    if ! test -f "$2/PLATFORM.c"; then
        cp ${LAVENDER_DIR}/tests/templates/source/PLATFORM.c "$2/PLATFORM.c"
    fi
}

update_core () {
    mkdir -p ${GAME_DIR}/tests/core/include
    mkdir -p ${GAME_DIR}/tests/core/source
    core_include=$(realpath "${GAME_DIR}/tests/core/include")
    core_source=$(realpath "${GAME_DIR}/tests/core/source")
    if [ $GAME_DIR != $LAVENDER_DIR ]; then
        ./update_recursive.sh \
            $core_dir \
            "" \
            $core_include \
            $core_source \
            "core" \
            "*/implemented*"
    else
        ./update_recursive.sh \
            $core_dir \
            "" \
            $core_include \
            $core_source \
            "core" \
            ""
    fi
    gen_main $core_include $core_source $1
}

update_core $1

if [ "$1" ]; then
    mkdir -p ${GAME_DIR}/tests/$1/include
    mkdir -p ${GAME_DIR}/tests/$1/source
    ./update_recursive.sh \
        $platform_dir \
        "" \
        ${GAME_DIR}/tests/$1/include \
        ${GAME_DIR}/tests/$1/source \
        $1 \
        "*/implemented*"
fi

if [[ $LAVENDER_DIR != $GAME_DIR ]]; then
    mkdir -p ${GAME_DIR}/tests/$(basename $GAME_DIR)/include
    mkdir -p ${GAME_DIR}/tests/$(basename $GAME_DIR)/source
    ./update_recursive.sh \
        ${GAME_DIR}/source \
        "" \
        $(basename $GAME_DIR)/include \
        $(basename $GAME_DIR)/source \
        $(basename $GAME_DIR) \
        ""
    exit 
fi
