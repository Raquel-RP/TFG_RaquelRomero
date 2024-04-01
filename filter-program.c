#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

SEC("filter")
int filter_func(struct __sk_buff *skb) {
    // Obtiene el puntero al encabezado Ethernet
    void *data = (void *)(long)skb->data;
    void *data_end = (void *)(long)skb->data_end;

    // Verifica que haya suficiente espacio para el encabezado Ethernet e IP
    if (data + sizeof(struct ethhdr) + sizeof(struct iphdr) > data_end)
        return TC_ACT_OK;

    // Obtiene el puntero al encabezado IP
    struct ethhdr *eth = data;
    struct iphdr *ip = data + sizeof(struct ethhdr);

    // Filtra paquetes marcados con la marca 0x1234
    if (skb->mark == 0x1234) {
        // Verifica si es un paquete IP
        if (eth->h_proto == htons(ETH_P_IP)) {
            // Verifica si es un paquete UDP
            if (ip->protocol == IPPROTO_UDP) {
                // Filtra el paquete
                return TC_ACT_SHOT;
            }
        }
    }

    return TC_ACT_OK;
}

char _license[] SEC("license") = "GPL";
