#include <iostream>

using namespace std;

#include "ConsoleStyle.h"
#define NLOG_PREFIX NLOG_CONSOLE_BOLD
#define NLOG_POSTFIX NLOG_CONSOLE_RESET

#define NLOG_ERROR_PREFIX NLOG_CONSOLE_FOREGROUND_RED
#define NLOG_INFO_PREFIX NLOG_CONSOLE_FOREGROUND_BLUE
#define NLOG_DEBUG_PREFIX NLOG_CONSOLE_FOREGROUND_GREEN

#define NLOG_OPT_PRINTF
#define NLOG_OPT_DEBUG

#include "NLog.h"

void __NLog_Report(nlog_object_id_t objectID, nlog_message_id_t messageID,
                   nlog_parameter_t param1, nlog_parameter_t param2,
                   nlog_parameter_t param3, nlog_parameter_t param4)
{
    cout << "[" << hex << objectID << ", " << messageID << "], " << dec
            << param1 << ", "
            << param2 << ", "
            << param3 << ", "
            << param4 << endl;
}

int main()
{
    cout << "This is a regular print" << endl;
    NLOG("This is a message.");
    NLOG_ERROR("This is an error message.");
    NLOG_INFO("This is an info message.");
    NLOG_DEBUG("This is a debug message.");

    NLOG("This is the %dth message.", 5);
    return 0;
}