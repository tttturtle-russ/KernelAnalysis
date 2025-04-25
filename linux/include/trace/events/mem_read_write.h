#include "linux/types.h"
#undef TRACE_SYSTEM
#define TRACE_SYSTEM mem_read_write

#if !defined(_TRACE_MEM_READ_WRITE_H) || defined(TRACE_HEADER_MULTI_READ)
#define _TRACE_MEM_READ_WRITE_H

#include <linux/tracepoint.h>

TRACE_EVENT(mem_read_write, 
    TP_PROTO(const volatile void* ip, const volatile void* ptr, size_t size, int type, size_t val), 
    TP_ARGS(ip, ptr, size, type, val), 
    TP_STRUCT__entry(
        __field( const volatile void*, ip)
		__field( const volatile void*, ptr)
		__field( size_t, size)
		__field( int, type)
        __field( size_t, val)
    ), 
    TP_fast_assign(
        __entry->ip = ip;
		__entry->ptr = ptr;
		__entry->size = size;
		__entry->type = type;
        __entry->val = val;
    ),
    TP_printk("ip=%px, ptr=%px, size=%d, type=%d, val=%u",
            __entry->ip, __entry->ptr, __entry->size, __entry->type, __entry->val)
);

#endif /* _TRACE_MEM_READ_WRITE_H */

#include <trace/define_trace.h>