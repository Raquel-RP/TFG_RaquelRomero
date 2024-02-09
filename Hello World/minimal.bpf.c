/* Este programa eBPF rastrea las llamadas al sistema write y registra información sobre el proceso que las realiza,
   aplicando un filtro opcional basado en el PID del proceso. 
*/

/* SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause) */
#define BPF_NO_GLOBAL_DATA      // Dehabilita el almacenamiento de datos globales en el programa BPF, no se pueden declarar var globales
#include <linux/bpf.h>          // define estructuras y funciones BPF
#include <bpf/bpf_helpers.h>    // Funciones de ayuda  
#include <bpf/bpf_tracing.h>    // Macros y definiciones de tracing eBPF

typedef unsigned int u32;
typedef int pid_t;
const pid_t pid_filter = 0;

char LICENSE[] SEC("license") = "Dual BSD/GPL";

SEC("tp/syscalls/sys_enter_write")  // Asociada con el evento sys_enter_write, se desencadena cada vez que se realiza una llamada al sistema write
int handle_tp(void *ctx)            // ctx contiene el contexto de la llamada al sistema
{
 pid_t pid = bpf_get_current_pid_tgid() >> 32;  // PID del proceso que hizo la llamada al sistema write
 // El PID se obtiene desplazando 32 bits hacia la derecha, ya que los 32 bits superiores de 
 // bpf_get_current_pid_tgid() contienen el TID (identificador de hilo), que no se utiliza en este caso.

 if (pid_filter && pid != pid_filter)
  return 0;
 bpf_printk("BPF triggered sys_enter_write from PID %d.\n", pid); // Imprime mensaje en el buffer de registro del kernel
 return 0;  // Necesario paar el funcionamiento correcto, indicar que la llamada al sistema write puede continuar normalmente
}