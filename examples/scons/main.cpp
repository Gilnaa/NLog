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

void __NLog_Report(nlog_message_id_t messageID,
                   uint32_t param1 = 0, uint32_t param2 = 0,
                   uint32_t param3 = 0, uint32_t param4 = 0)
{
    cout << "[" << hex << messageID << dec << "], "
            << param1 << ", "
            << param2 << ", "
            << param3 << ", "
            << param4 << endl;
}

int main()
{
    NLOG("This is a message.");
    NLOG("This is a message.");
    NLOG("This is a message.");
    cout << "This is a regular print" << endl;
    return 0;
}