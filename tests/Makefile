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

export DIR_PLATFORM := $(BASE_DIR)/$(PLATFORM)
export CORE_OMIT := main.c
include $(DIR_CORE)/Makefile.include
ifneq ($(PLATFORM),)
include $(DIR_PLATFORM)/Makefile.include
else
INCLUDE_PLATFORM += $(CURDIR)/templates/include
SOURCE_PLATFORM += $(CURDIR)/templates/source
endif

#---------------------------------------------------------------------------------
# TARGET is the name of the output
# BUILD is the directory where object files & intermediate files will be placed
# SOURCE is the directory containing source code
# INCLUDES is a list of directories containing extra header files
# ASSETS is the directory of assets
#---------------------------------------------------------------------------------
export TARGET  	:= $(shell basename $(BASE_DIR))
export SOURCE_TEST_CORE   := $(CURDIR)/core/source
export INCLUDE_TEST_CORE   := $(CURDIR)/core/include
export DATA     := data

ifneq ($(PLATFORM),)
export INCLUDE_TEST_PLATFORM   := $(CURDIR)/$(PLATFORM)/include
export SOURCE_TEST_PLATFORM   := $(CURDIR)/$(PLATFORM)/source
export CFILES_TEST_PLATFORM != realpath \
	--relative-to=$(SOURCE_TEST_PLATFORM) \
	$$(find $(SOURCE_TEST_PLATFORM) -name \*.c)
export OFILES_TEST_PLATFORM := \
  $(CFILES_TEST_PLATFORM:.c=.o)
endif

export INCLUDES := $(SOURCE_CORE) $(INCLUDE_CORE) \
	$(SOURCE_PLATFORM) $(INCLUDE_PLATFORM) \
	$(INCLUDE_TEST_CORE) $(INCLUDE_TEST_PLATFORM) \

export OUTPUT 	:= $(BUILD)/$(TARGET)
export DEPSDIR 	:= $(BUILD)

export CFILES_TEST_CORE != realpath \
	--relative-to=$(SOURCE_TEST_CORE) \
	$$(find $(SOURCE_TEST_CORE) -name \*.c)
export SFILES       := $(shell find $(SOURCE_TEST_CORE) -name *.s)

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
	$(OFILES_TEST_PLATFORM)

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
	@$(ADD_COMPILE_COMMAND) end

#---------------------------------------------------------------------------------
else

#---------------------------------------------------------------------------------
# main targets
#---------------------------------------------------------------------------------

$(OUTPUT): $(OFILES)
	$(SILENT)$(LD) $(LDFLAGS) $(FLAGS_LINKER) $(OFILES) $(LIBPATHS) $(LIBS) -o $@
	@$(ADD_COMPILE_COMMAND) add $(CC) "$(CFLAGS) $(LIBS) $(INCLUDE) $(FLAGS) \
		-o $(BUILD)/$@ -c $(SOURCE_CORE)/$(@:.o=.c)" $(BUILD)/$@

#---------------------------------------------------------------------------------
$(CFILES_TEST_CORE:.c=.o) : $(foreach file,$(CFILES),$(BASE_DIR)/tests/core/source/$(file))
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(INCLUDE) $(FLAGS) -c $(BASE_DIR)/tests/core/source/$(basename $@).c -o $@
ifneq ($(PLATFORM),)
$(CFILES_TEST_PLATFORM:.c=.o) : $(foreach file,$(CFILES),$(BASE_DIR)/tests/$(PLATFORM)/source/$(file))
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) $(INCLUDE) $(FLAGS) -c $(BASE_DIR)/tests/$(PLATFORM)/source/$(basename $@).c -o $@
endif
#---------------------------------------------------------------------------------

-include $(DEPSDIR)/*.d

#---------------------------------------------------------------------------------------
endif
#---------------------------------------------------------------------------------------
