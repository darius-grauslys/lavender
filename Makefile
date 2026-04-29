
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

.PHONY: test clean check-file compile_commands

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
	@echo "-DIS_SERVER 	-	treat build as a server."
	@echo "-DNDEBUG		-	disable debug, performant but most errors will result in a crash now!"
	@echo "-ggdb		-	generate gdb debug symbols - required for gdb."
	@echo "-DNLOG		-	disable logging, keep debug safety checks."
else
default:
	$(SILENT)bear --output ./compile_commands.json --force-preload \
		-- make -f $(LAVENDER_DIR)/Makefile.build $(BUILD)
endif

# compile_commands: Generate compile_commands.json without a full build.
# Uses bear with make -n (dry-run) via --force-wrapper mode.
# Requires PLATFORM to be set.
compile_commands:
ifndef PLATFORM
	$(error Usage: make compile_commands -e PLATFORM=sdl)
endif
	$(SILENT)bear --output ./compile_commands.json --force-wrapper \
		-- make -f $(LAVENDER_DIR)/Makefile.build $(BUILD)

# check-file: Spot-build a single module with -fsyntax-only for validation.
# Accepts absolute paths or paths relative to CWD.
# Usage: make check-file FILE=core/source/rendering/graphics_window.c -e PLATFORM=sdl
check-file:
ifndef FILE
	$(error Usage: make check-file FILE=path/to/file.c -e PLATFORM=sdl)
endif
ifndef PLATFORM
	$(error check-file requires PLATFORM. Usage: make check-file FILE=path/to/file.c -e PLATFORM=sdl)
endif
	$(SILENT)make -f $(LAVENDER_DIR)/Makefile.build check-file FILE=$(FILE)

test:
	$(SILENT)if [ $(GAME_DIR) != $(LAVENDER_DIR) ]; then \
		sh -c "cp -r ${LAVENDER_DIR}/tests ./"; \
	fi
	@sh -c "cd ./tests && ./update.sh $(PLATFORM)"
	$(SILENT)if [ -z "${PLATFORM}" ]; then \
		mkdir -p ./build \
		&& bear --output $(GAME_DIR)/compile_commands.json --force-preload \
			-- make -C $(GAME_DIR)/tests \
			-f $(LAVENDER_DIR)/tests/Makefile \
			-e BUILD=$(GAME_DIR)/build/test_core\
				DIR_CORE=$(LAVENDER_DIR)/core; \
	else \
		mkdir -p ./build \
		&& bear --output $(GAME_DIR)/compile_commands.json --force-preload \
			-- make \
				-C $(GAME_DIR)/tests \
				-f $(LAVENDER_DIR)/tests/Makefile \
				-e BUILD=$(GAME_DIR)/build/test_$(PLATFORM) \
					DIR_CORE=$(LAVENDER_DIR)/core \
					PLATFORM=$(PLATFORM); \
	fi

clean:
	@echo clean...
	@if [ -e "./build" ]; then \
		rm -r ./build ; \
	fi
