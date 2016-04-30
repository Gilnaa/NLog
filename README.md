# NLog #
NLog is logger front-end that allows an executable to maintain small size, but still allow the developer to include detailed log messages.

The core library is a single header (`NLog.h`), and contains all the code that needs to be compiled into the executable.

To log a message using the logger, all you have to do is call the NLOG macro, supplying a string and up to 4 optional integer arguments.

## What does it do? ##

Not much.

During compile time, the string will be assigned two 32-bit indicies, and will be stored in a special section in the ELF file.
The indicies and the arguments are than passed to a user implemeted function that does the actuall logging (`__NLog_Report`).

The rest of the magic happens after compilation. A script called `scrub.py` runs and produces a dictionary, mapping the indicies to the messages. It then removes all the NLog-generated strings and metadata from the ELF file.

## Integration ##
In order to use NLog, there are a few thing the developer has to do.

### Logging ###
The first thing that needs to be done, is to implement the logging function.
NLog doesn't do the actual logging, it only wraps it. 

The user has to implement the following function.
The details of actual logging are not important, and are up to the developer to decide.
```
extern void __NLog_Report(nlog_object_id_t,
                          nlog_message_id_t,
                          nlog_parameter_t,
                          nlog_parameter_t,
                          nlog_parameter_t,
                          nlog_parameter_t);
```

### Build-System ###
NLog requires build-system integration.

#### Source Compilation ####
For each source file compiled, a unique ID should be generated and injected as a preprocessor symbol (using GCC's `-D`). 
The ID is an unsigned 32bit, and the injected-format has to be comply with the `%#08x` format string. (e.g. 0xDEADBEEF)

The included example shows how to integrate NLog with an SCons project.
The used ID is a CRC32 value calculated using the file name, but any value is applicable as long as it is unique between source files.

#### Post-Build ####
After a successfull build, the resulting executable (or library), must be modifyed by the `scrub.py`, which extracts the log messages from the ELF into a seperate dictionary, and then proceeds to clean the ELF.

## What is it good for? ##
~~Absolutely nothing~~
NLog is not for everyone. To be honest, it probably doesn't suit most application, but it has two very important advantages.

The first one is of course the smaller binary size.
A small memory footprint is not always sought for, but this is critical for embedded devices and systems low on resources.
Not only the each log entry is small, but they all have the exact same size.

The second one is the fact that the resulting binary contains no textual information that might aid a potential attacker trying to reverse engineer it.

## How does it look like? ##
```c
bool DoSomeComplexOperation(void *somePointer, uint32_t someInteger)
{
    if ((somePointer == NULL) || (someInteger > MAX_SIZE))
    {
        NLOG("DoSomeComplexOperation failed due to invalid arguments");
        return false;
    }

    // ... 

    if (!AnotherComplexFunction(somePointer, &someInteger))
    {
        NLOG("DoSomeComplexOperation failed because of AnotherComplexFunction");
        return false;
    }

    // ...

    NLOG("DoSomeComplexOperation finished successfully with an exit code of %u", someInteger);

    return true;
}
```
## Variants ##
Beside of the NLOG macro, there are a few more macros:
 - NLOG_ERROR: For logging of critical errors and failures.
 - NLOG_INFO: For logging of additional information.
 - NLOG_DEBUG: For logging of debbuging information.

The debug log can be disabled during compile time. If it is disabled, no strings will be created and no entries will be logged.

Each of the variants' string formatting is configurable, as seen in the "Options" section.

## Options ##
The logger front-end is configurable through the definition of several pre-processor symbols.

### Prefix ###
A prefix is prepended to each of the log messages.
`NLOG_PREFIX` is prepended to all of the log messages, while `NLOG_ERROR_PREFIX`, `NLOG_INFO_PREFIX`, and `NLOG_DEBUG_PREFIX` are prepended to their respective `NLOG_*` macros.

### Postfix ###
A postfix is appended to each of the log messages.
`NLOG_POSTFIX` is appended to all of the log messages, while `NLOG_ERROR_POSTFIX`, `NLOG_INFO_POSTFIX`, and `NLOG_DEBUG_POSTFIX` are appended to their respective `NLOG_*` macros.

### Parameters ###
The parameter type is configurable by defining the `NLOG_OPT_PARAM_TYPE` symbol.
If remained undefined, the parameter type will be `uint32_t`.
The type can be any valid C / C++ type, including references and pointers, but it must be defined before the inclusion of the NLog header.

Its default value of an unspecified paramter is configurable by `NLOG_OPT_DEFAULT_PARAM_VALUE` (which is 0, by default).

### PrintF ###
The library can print the strings instead of generating genuine NLog calls.
If the `NLOG_OPT_PRINTF` symbol is defined, all of the log data will be printed to stderr. The parameters are passed as formatting arguments.

### Debug Logs ###
By default, debug logs would be ignored, both during compile-time and runtime.
In order to compile these logs in, the `NLOG_OPT_DEBUG` must be defined.

## Colors ##
Along with the single `NLog.h` header, required by the library, a second `ConsoleStyle.h` header is included.

This header defines common console escape codes that can be used to style the output.

Example:
```c
#include "ConsoleStyle.h"
#define NLOG_PREFIX NLOG_CONSOLE_BOLD
#define NLOG_POSTFIX NLOG_CONSOLE_RESET

#define NLOG_ERROR_PREFIX NLOG_CONSOLE_FOREGROUND_RED
#define NLOG_INFO_PREFIX NLOG_CONSOLE_FOREGROUND_BLUE
#define NLOG_DEBUG_PREFIX NLOG_CONSOLE_FOREGROUND_GREEN

#define NLOG_OPT_PRINTF
#define NLOG_OPT_DEBUG

#include "NLog.h"
```