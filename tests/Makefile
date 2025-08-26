#---------------------------------------------------------------------------------
.SUFFIXES:
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
# options for code generation
#---------------------------------------------------------------------------------
CFLAGS := -Wall -O2

CFLAGS    += $(INCLUDE)

LDFLAGS  = 

#---------------------------------------------------------------------------------
# any extra libraries we wish to link with the project (order is important)
#---------------------------------------------------------------------------------
LIBS :=  $(PLATFORM_LIBS)

#---------------------------------------------------------------------------------
# list of directories containing libraries, this must be the top level containing
# include and lib
#---------------------------------------------------------------------------------
LIBDIRS := 

#---------------------------------------------------------------------------------
# no real need to edit anything past this point unless you need to add additional
# rules for different file extensions
#---------------------------------------------------------------------------------
ifneq ($(BUILD),$(CURDIR))
#---------------------------------------------------------------------------------

export DIR_PLATFORM := $(LAVENDER_DIR)/$(PLATFORM)
export CORE_OMIT := main.c
include $(DIR_CORE)/Makefile.include
ifneq ($(PLATFORM),)
include $(DIR_PLATFORM)/Makefile.include
else
INCLUDE_PLATFORM += $(LAVENDER_DIR)/tests/templates/include
SOURCE_PLATFORM += $(LAVENDER_DIR)/tests/templates/source
endif

#---------------------------------------------------------------------------------
# TARGET is the name of the output
# BUILD is the directory where object files & intermediate files will be placed
# SOURCE is the directory containing source code
# INCLUDES is a list of directories containing extra header files
# ASSETS is the directory of assets
#---------------------------------------------------------------------------------
export TARGET  	:= $(shell basename $(GAME_DIR))
export SOURCE_TEST_CORE   := $(GAME_DIR)/tests/core/source
export INCLUDE_TEST_CORE   := $(GAME_DIR)/tests/core/include
export DATA     := data

ifneq ($(PLATFORM),)
export INCLUDE_TEST_PLATFORM   := $(GAME_DIR)/tests/$(PLATFORM)/include
export SOURCE_TEST_PLATFORM   := $(GAME_DIR)/tests/$(PLATFORM)/source
export CFILES_TEST_PLATFORM != realpath \
	--relative-to=$(SOURCE_TEST_PLATFORM) \
	$$(find $(SOURCE_TEST_PLATFORM) -name \*.c)
export OFILES_TEST_PLATFORM := \
  $(CFILES_TEST_PLATFORM:.c=.o)
endif

ifneq ($(LAVENDER_DIR),$(GAME_DIR))
export SOURCE_GAME := $(GAME_DIR)/source
export INCLUDE_GAME := $(GAME_DIR)/include
export INCLUDE_TEST_GAME := $(GAME_DIR)/tests/$(shell basename $(GAME_DIR))/include
export SOURCE_TEST_GAME := $(GAME_DIR)/tests/$(shell basename $(GAME_DIR))/source

export CFILES_TEST_GAME != realpath \
	--relative-to=$(SOURCE_TEST_GAME) \
	$$(find $(SOURCE_TEST_GAME) -name \*.c)

export OFILES_TEST_GAME := \
  $(CFILES_TEST_GAME:.c=.o)
endif

export INCLUDES := \
	$(SOURCE_GAME) $(INCLUDE_GAME) \
	$(SOURCE_PLATFORM) $(INCLUDE_PLATFORM) \
	$(SOURCE_CORE) $(INCLUDE_CORE) \
	$(INCLUDE_TEST_GAME) $(INCLUDE_TEST_PLATFORM) $(INCLUDE_TEST_CORE) \

export OUTPUT 	:= $(BUILD)/$(TARGET)
export DEPSDIR 	:= $(BUILD)

ifneq ($(LAVENDER_DIR),$(GAME_DIR))
export CFILES_TEST_CORE != realpath \
	--relative-to=$(SOURCE_TEST_CORE) \
	$$(find $(SOURCE_TEST_CORE) -name \*.c -not -path */implemented/*)
else
export CFILES_TEST_CORE != realpath \
	--relative-to=$(SOURCE_TEST_CORE) \
	$$(find $(SOURCE_TEST_CORE) -name \*.c)
endif

#---------------------------------------------------------------------------------
# use CXX for linking C++ projects, CC for standard C
#---------------------------------------------------------------------------------
ifeq ($(strip $(CPPFILES)),)
#---------------------------------------------------------------------------------
  export LD := $(CC)
#---------------------------------------------------------------------------------
else
#---------------------------------------------------------------------------------
  export LD := $(CXX)
#---------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------

export OFILES_TEST_CORE := \
  $(CFILES_TEST_CORE:.c=.o)

export OFILES := \
	$(addsuffix .o,$(BINFILES)) \
	$(OFILES_TEST_CORE)\
	$(OFILES_TEST_PLATFORM)\
	$(OFILES_TEST_GAME)

export INCLUDE := \
  $(foreach dir,$(INCLUDES),-I$(dir)) \
  $(foreach dir,$(LIBDIRS),-I$(dir)/include) \
  -I$(BUILD)/$(ASSETS)\
  -I$(BUILD)

export LIBPATHS := $(foreach dir,$(LIBDIRS),-L$(dir)/lib)

.PHONY: $(BUILD) clean 

#---------------------------------------------------------------------------------
$(BUILD):
	@[ -d $@ ] || mkdir -p $@
	@$(MAKE) --no-print-directory -C $(BUILD) -f $(CURDIR)/Makefile \
		 | grep -wE 'cc|gcc|g\+\+' \
		 | grep -w '\-c' \
		 | jq -nR '[inputs|{directory:"$(BUILD)", command:., file: match(" [^ ]+$$").string[1:]}]' \
		 > $(BUILD)/compile_commands.json

#---------------------------------------------------------------------------------
else

#---------------------------------------------------------------------------------
# main targets
#---------------------------------------------------------------------------------

$(OUTPUT): $(OFILES)
	$(SILENT)$(LD) $(LDFLAGS) $(FLAGS_LINKER) $(OFILES) $(LIBPATHS) $(LIBS) -o $@
	@$(ADD_COMPILE_COMMAND) end

#---------------------------------------------------------------------------------
$(CFILES_TEST_CORE:.c=.o) : $(foreach file,$(CFILES),$(GAME_DIR)/tests/core/source/$(file))
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(INCLUDE) $(FLAGS) -c $(GAME_DIR)/tests/core/source/$(basename $@).c -o $@
	@$(ADD_COMPILE_COMMAND) add $(CC) "$(CFLAGS) $(LIBS) $(INCLUDE) $(FLAGS) \
		-o $(BUILD)/$@ -c $(SOURCE_CORE)/$(@:.o=.c)" $(BUILD)/$@
ifneq ($(PLATFORM),)
$(CFILES_TEST_PLATFORM:.c=.o) : $(foreach file,$(CFILES),$(GAME_DIR)/tests/$(PLATFORM)/source/$(file))
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(INCLUDE) $(FLAGS) -c $(GAME_DIR)/tests/$(PLATFORM)/source/$(basename $@).c -o $@
	@$(ADD_COMPILE_COMMAND) add $(CC) "$(CFLAGS) $(LIBS) $(INCLUDE) $(FLAGS) \
		-o $(BUILD)/$@ -c $(SOURCE_PLATFORM)/$(@:.o=.c)" $(BUILD)/$@
endif
$(CFILES_TEST_GAME:.c=.o) : $(foreach file,$(CFILES),$(GAME_DIR)/tests/$(shell basename $(GAME_DIR))/source/$(file))
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(INCLUDE) $(FLAGS) -c $(GAME_DIR)/tests/$(shell basename $(GAME_DIR))/source/$(basename $@).c -o $@
	@$(ADD_COMPILE_COMMAND) add $(CC) "$(CFLAGS) $(LIBS) $(INCLUDE) $(FLAGS) \
		-o $(BUILD)/$@ -c $(shell basename $(GAME_DIR))/source/$(@:.o=.c)" $(BUILD)/$@
#---------------------------------------------------------------------------------

-include $(DEPSDIR)/*.d

#---------------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------------
