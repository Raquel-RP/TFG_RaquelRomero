#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/pkt_cls.h>
#include <bpf/bpf_endian.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

SEC("tc")

int filter_func(struct __sk_buff *skb) {

    // Filtra paquetes marcados con la marca 0x1234
    if (skb->mark == 0x1234) {
        return TC_ACT_SHOT;

    }

    return TC_ACT_OK;
}

char __license[] SEC("license") = "GPL";
