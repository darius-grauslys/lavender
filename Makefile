
# Assignment operators in Makefile:
# 	Note: all variables work as inline subsitution.
# "=" 	- 	Recursive assignment. If there are variables referenced in the RValue
# 			then when the assigned variable is used, it will recursively evaluate
# 			the RValue at the time of inlining.
#
# ":="	-	Literal assignment. Any and all variables in the RValue is subsituted
# 			at the time of assignment. No recurison will happen when inlining this
# 			assigned variable.
#
# "!="	-	Shell assignment. This will treat the RValue is a shell command and run it.
# 			The output then becomes the RValue.

.PHONY: nds test_nds sdl unix_opengl test_unix_opengl clean

export BASE_DIR := $(CURDIR)

export SILENT := @

export DIR_NDS := $(CURDIR)/nds
export DIR_UNIX_OPENGL := $(CURDIR)/unix_opengl
export DIR_SDL := $(CURDIR)/sdl
export DIR_CORE := $(CURDIR)/core

export DIR_TEST_CORE := $(CURDIR)/tests/core

export BUILD_NDS := $(CURDIR)/build/nds
export BUILD_SDL := $(CURDIR)/build/sdl
export BUILD_TEST_CORE := $(CURDIR)/build/test_core
export BUILD_TEST_SDL := $(CURDIR)/build/test_sdl

GENERATE_COMPILE_COMMANDS := 1
ifeq ($(GENERATE_COMPILE_COMMANDS),1)
    export ADD_COMPILE_COMMAND := $(BASE_DIR)/generate_compile_commands
else
	export ADD_
endif

default:
	echo "--- Targets ---"
	echo "test_[PLATFORM] 	-	make corresponding tests for given platform."
	echo "sdl				-	SDL2, see sdl/README for supported systems."
	echo "nds				-	Native 2D engine NDS platform"
	echo ""
	echo "--- Useful FLAGS ---"
	echo "X: anything, NA: omit to disable"
	echo "-DIS_SERVER 	-	treat build as a server"
	echo "-DNDEBUG		-	disable debug, performant but most errors will result in a crash now!"
	echo "-ggdb			-	generate gdb debug symbols - required for gdb"

nds:
	$(SILENT)mkdir -p ./build && make -C $(CURDIR)/nds -f $(CURDIR)/nds/Makefile -e BUILD=$(BUILD_NDS)
	$(SILENT)stat $(BUILD_NDS)/compile_commands.json && ln -sf $(BUILD_NDS)/compile_commands.json ./compile_commands.json

test_nds:
	$(SILENT)mkdir -p ./build && make -C $(CURDIR)/nds -f $(CURDIR)/nds/Makefile -e BUILD=$(CURDIR)/build/test_nds
	$(SILENT)stat $(BUILD_TEST_NDS)/compile_commands.json && ln -sf $(BUILD_TEST_NDS)/compile_commands.json ./compile_commands.json

sdl:
	$(SILENT)mkdir -p ./build && make -C $(CURDIR)/sdl -f $(CURDIR)/sdl/Makefile -e BUILD=$(BUILD_SDL)
	$(SILENT)stat $(BUILD_SDL)/compile_commands.json && ln -sf $(BUILD_SDL)/compile_commands.json ./compile_commands.json

test:
	$(SILENT)if [ -z "${PLATFORM}" ]; then \
		mkdir -p ./build && make -C $(DIR_TEST_CORE) -f $(DIR_TEST_CORE)/Makefile -e BUILD=$(BUILD_TEST_CORE); \
		stat $(BUILD_TEST_CORE)/compile_commands.json && ln -sf $(BUILD_TEST_CORE)/compile_commands.json ./compile_commands.json; \
	else \
		mkdir -p ./build && make \
			-C $(CURDIR)/tests \
			-f $(CURDIR)/tests/Makefile \
			-e BUILD=$(CURDIR)/build/test_$(PLATFORM) \
				DIR_CORE=$(CURDIR)/core \
				PLATFORM=$(PLATFORM); \
		stat $(CURDIR)/build/test_$(PLATFORM)/compile_commands.json \
			&& ln -sf $(CURDIR)build/test_$(PLATFORM)/compile_commands.json ./compile_commands.json; \
	fi

clean:
	@echo clean...
	@if [ -e "./build/*" ]; then \
		rm -r ./build/* ; \
	fi

