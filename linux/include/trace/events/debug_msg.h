#undef TRACE_SYSTEM
#define TRACE_SYSTEM debug_msg

#if !defined(_TRACE_DEBUG_MSG_H) || defined(TRACE_HEADER_MULTI_READ)
#define _TRACE_DEBUG_MSG_H

#include <linux/tracepoint.h>

TRACE_EVENT(debug_msg, 
    TP_PROTO(const char* msg), 
    TP_ARGS(msg), 
    TP_STRUCT__entry(
        __string(msg, msg)
    ), 
    TP_fast_assign(
        __assign_str(msg, msg)
    ),
    TP_printk("DEUBG: msg: %s", __get_str(msg))
);

#endif /* _TRACE_DEBUG_MSG_H */

#include <trace/define_trace.h>