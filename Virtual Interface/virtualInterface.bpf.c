#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/in.h>
#include <bpf/bpf_helpers.h>

// Definiciones de variables
#define MY_CGROUP_ID 100
#define MY_IPV4_ADDRESS 0x0A000001  // Dirección IPv4 10.0.0.1
#define INTERFACE_INDEX 3  // Índice de la interfaz virtual deseada

// Definir un mapa de arrays per-cpu de BPF para almacenar el buffer
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __type(key, int);
    __type(value, char[ETH_FRAME_LEN]);
} packet_buffer_map SEC(".maps");

SEC("cgroup_skb/ingress")
int redirect_packets(struct __sk_buff *skb)
{
    // Obtenemos un puntero al buffer per-cpu para el paquete
    char *packet_buffer = bpf_map_lookup_elem(&packet_buffer_map, &skb->ifindex);
    if (!packet_buffer)
        return 0; // No se pudo obtener el buffer

    // Obtenemos los bytes del paquete
    bpf_skb_load_bytes(skb, 0, packet_buffer, sizeof(packet_buffer));

    // Obtenemos el IP header del paquete dentro del buffer
    struct iphdr *ip_header = (struct iphdr *)(packet_buffer + sizeof(struct ethhdr));

    // Filtramos solo paquetes IPv4 salientes (dirección de origen en el cgroup)
    if (bpf_skb_cgroup_id(skb) != MY_CGROUP_ID || ip_header->saddr != MY_IPV4_ADDRESS)
        return 0; // No coincide con el cgroup y la dirección IP especificada

    // Redirigimos el paquete a la interfaz virtual
    bpf_redirect(INTERFACE_INDEX, 0);

    return 0; // Paquete procesado exitosamente
}

char _license[] SEC("license") = "GPL";
