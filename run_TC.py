from bcc import BPF
from ctypes import *

# Carga el programa eBPF desde el archivo objeto filter_program.o
b = BPF(src_file="filter_program.c")

# Adjunta el programa eBPF a la interfaz nflog0 para filtrar paquetes
b.attach_raw_socket("nflog")

# Mantén el programa en ejecución para que filtre los paquetes entrantes en nflog0
while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        break
