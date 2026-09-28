/* eBPF program: Memory telemetry
 * RAM usage, swap, page faults, NUMA locality, bandwidth
 */

#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

char LICENSE[] SEC("license") = "GPL";

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, __u32);
    __type(value, __u64);
} page_faults SEC(".maps");

SEC("tracepoint/exceptions/page_fault_user")
int handle_page_fault(struct trace_event_raw_sys_enter *ctx)
{
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u64 *count = bpf_map_lookup_elem(&page_faults, &pid);
    __u64 new_count = 1;
    if (count)
        new_count = *count + 1;
    bpf_map_update_elem(&page_faults, &pid, &new_count, BPF_ANY);
    return 0;
}
