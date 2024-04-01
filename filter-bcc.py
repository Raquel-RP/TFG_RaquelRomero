#!/usr/bin/env python3

# Copyright (c) PLUMgrid, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")

from bcc import BPF
from pyroute2 import IPRoute

ipr = IPRoute()

program = """
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/pkt_cls.h>


int filter_func(struct __sk_buff *skb) {
    // Filtra paquetes marcados con la marca 0x1234
    if (skb->mark == 0x1234) {
        return TC_ACT_SHOT;
    }
    return TC_ACT_OK;
}

"""

try:
    b = BPF(text=program, debug=0)
    fn = b.load_func("filter_func", BPF.SCHED_CLS)
    ipr.link("add", ifname="t1a", kind="veth", peer="t1b")
    idx = ipr.link_lookup(ifname="t1a")[0]

    ipr.tc("add", "ingress", idx, "ffff:")
    ipr.tc("add-filter", "bpf", idx, ":1", fd=fn.fd,
           name=fn.name, parent="ffff:", action="ok", classid=1)
    ipr.tc("add", "sfq", idx, "1:")
    ipr.tc("add-filter", "bpf", idx, ":1", fd=fn.fd,
           name=fn.name, parent="1:", action="ok", classid=1)
finally:
    if "idx" in locals(): ipr.link("del", index=idx)
print("BPF tc functionality - SCHED_CLS: OK")
