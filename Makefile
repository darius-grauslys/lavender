
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

.PHONY: test clean

export BASE_DIR := $(LAVENDER_DIR)

export SILENT := @

export GAME_INCLUDE_DIR?=$(BASE_DIR)
export GAME_SOURCE_DIR?=$(BASE_DIR)

ifeq ($(GAME_DIR),)
	export GAME_DIR=$(BASE_DIR)
endif

export BUILD=$(GAME_DIR)/build/$(PLATFORM)
ifeq ($(GAME),)
	export GAME=$(basename $(notdir $(GAME_DIR)))
endif

GENERATE_COMPILE_COMMANDS := 1
ifeq ($(GENERATE_COMPILE_COMMANDS),1)
    export ADD_COMPILE_COMMAND := $(BASE_DIR)/generate_compile_commands
else
endif

ifeq ($(PLATFORM),)
default:
	@echo "--- Targets ---"
	@echo "Specify with -e PLATFORM={platform}"
	@echo "test 		-	make corresponding tests for given {-DPLATFORM}, omit for just core testing."
	@echo "no_gui		-	No graphics good for server/bot."
	@echo "sdl			-	SDL2, see sdl/README for supported systems."
	@echo "nds			-	Native 2D engine NDS platform"
	@echo ""
	@echo "--- Useful FLAGS ---"
	@echo "X: anything, NA: omit to disable."
	@echo "-DPLATFORM	- 	specify target platform. DONT USE."
	@echo "-DIS_SERVER 	-	treat build as a server."
	@echo "-DNDEBUG		-	disable debug, performant but most errors will result in a crash now!"
	@echo "-ggdb		-	generate gdb debug symbols - required for gdb."
	@echo "-DNLOG		-	disable logging, keep debug safety checks."
else
default:
	$(SILENT)make -f $(LAVENDER_DIR)/Makefile.build $(BUILD)
	$(SILENT)stat $(BUILD)/compile_commands.json && ln -sf $(BUILD)/compile_commands.json ./compile_commands.json
endif

test:
	sh -c "cd ./tests && ./update.sh $(PLATFORM)"
	$(SILENT)if [ -z "${PLATFORM}" ]; then \
		mkdir -p ./build \
		&& make -C $(LAVENDER_DIR)/tests \
		-f $(LAVENDER_DIR)/tests/Makefile \
		-e BUILD=$(LAVENDER_DIR)/build/test_core; \
		stat $(BUILD_TEST_CORE)/compile_commands.json \
		&& ln -sf $(LAVENDER_DIR)/build/test_core/compile_commands.json ./compile_commands.json; \
	else \
		mkdir -p ./build && make \
			-C $(LAVENDER_DIR)/tests \
			-f $(LAVENDER_DIR)/tests/Makefile \
			-e BUILD=$(LAVENDER_DIR)/build/test_$(PLATFORM) \
				DIR_CORE=$(LAVENDER_DIR)/core \
				PLATFORM=$(PLATFORM); \
		stat $(LAVENDER_DIR)/build/test_$(PLATFORM)/compile_commands.json \
			&& ln -sf $(LAVENDER_DIR)build/test_$(PLATFORM)/compile_commands.json ./compile_commands.json; \
	fi

clean:
	@echo clean...
	@if [ -e "./build" ]; then \
		rm -r ./build ; \
	fi

