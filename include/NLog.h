/**
 * @file NLog.h
 *
 * @author  gilnaa
 * @since   29/04/2016
 */

#ifndef NLOG_NLOG_H
#define NLOG_NLOG_H

#include <stdint.h>

// Avoid ugly warnings for format.
#pragma GCC system_header
/**
 * Misc. Macros
 */
// Implementation
#define TAKE4(a1, a2, a3, a4, ...) a1, a2, a3, a4
#define NLOG_FILL_PARAMS(default_value, ...) TAKE4( __VA_ARGS__ + 0, default_value, default_value, default_value, default_value)

#define STRINGIFY_IMPL(v) #v
#define NLOG_STRINGIFY(v) STRINGIFY_IMPL(v)

// Settings
#ifndef NLOG_PREFIX
# define NLOG_PREFIX
#endif
#ifndef NLOG_POSTFIX
# define NLOG_POSTFIX
#endif

#ifndef NLOG_ERROR_PREFIX
# define NLOG_ERROR_PREFIX
#endif
#ifndef NLOG_ERROR_POSTFIX
# define NLOG_ERROR_POSTFIX
#endif

#ifndef NLOG_INFO_PREFIX
# define NLOG_INFO_PREFIX
#endif
#ifndef NLOG_INFO_POSTFIX
# define NLOG_INFO_POSTFIX
#endif

#ifndef NLOG_DEBUG_PREFIX
# define NLOG_DEBUG_PREFIX
#endif
#ifndef NLOG_DEBUG_POSTFIX
# define NLOG_DEBUG_POSTFIX
#endif

#ifndef NLOG_OPT_PARAM_TYPE
# define NLOG_OPT_PARAM_TYPE uint32_t
#endif

#ifndef NLOG_OPT_DEFAULT_PARAM_VALUE
# define NLOG_OPT_DEFAULT_PARAM_VALUE 0
#endif

#ifndef NLOG_OPT_REPORT_FUNCTION
# define NLOG_OPT_REPORT_FUNCTION __NLog_Report
#endif
/**
 * Types & prototypes
 */
typedef uint64_t nlog_message_id_t;

/**
 * Implementation
 */

#define NLOG_ID_IMPL(counter, id) 0x ## counter ## id
#define NLOG_ID(counter, id) NLOG_ID_IMPL(counter, id)

// Note to self: DO NOT REPLACE m[] WITH *m BECAUSE IT WILL FUCK YOU UP!
#define NLOG_TEXT_SECTION(msg, id) static const char m[] __attribute__((section(".nlog-msg-" NLOG_STRINGIFY(id)))) = NLOG_PREFIX msg NLOG_POSTFIX

#if defined(NLOG_OPT_PRINTF)
#include <stdio.h>
#define NLOG_IMPL(id, msg, ...) ({\
                                    NLOG_TEXT_SECTION(msg, id);\
                                    fprintf(stderr, NLOG_PREFIX msg NLOG_POSTFIX "\n", ##__VA_ARGS__);\
                                    id;\
                                })

#else
#define NLOG_IMPL(id, msg, ...) ({\
                                    NLOG_TEXT_SECTION(msg, id);\
                                    id;\
                                })
#endif

#define NLOG_IMPL_REPORT(id, msg, ...) ({\
                                            NLOG_OPT_REPORT_FUNCTION(id, ##__VA_ARGS__);\
                                            NLOG_IMPL(id, msg, ##__VA_ARGS__);\
                                        })

# define NLOG(msg, ...) NLOG_IMPL_REPORT(NLOG_ID(__COUNTER__, NLOG_OBJECT_ID), msg, ##__VA_ARGS__)

#define NLOG_ERROR(msg, ...) NLOG(NLOG_ERROR_PREFIX msg NLOG_ERROR_POSTFIX, ##__VA_ARGS__)
#define NLOG_INFO(msg, ...) NLOG(NLOG_INFO_PREFIX msg NLOG_INFO_POSTFIX, ##__VA_ARGS__)

#if defined(NLOG_OPT_DEBUG)
# define NLOG_DEBUG(msg, ...) NLOG(NLOG_DEBUG_PREFIX msg NLOG_DEBUG_POSTFIX, ##__VA_ARGS__)
#else
# define NLOG_DEBUG(...)
#endif

#endif //NLOG_NLOG_H
