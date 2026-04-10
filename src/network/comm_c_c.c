#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/select.h>

/* --- CONFIGURATION DES PORTS --- */
#define PY_HOST         "127.0.0.1"
#define PY_PORT         1030    // C envoie les données vers Python
#define C_PORT          1040    // Python envoie les données vers C
#define LAN_PORT        4950    // Port de diffusion (Broadcast) sur le réseau local
#define BUFLEN          2048    // Taille maximale des messages JSON

int main() {
    int sock_lan, sock_ipc;
    struct sockaddr_in addr_lan, addr_ipc, addr_py, addr_broadcast;
    char tampon[BUFLEN];
    fd_set ensemble_fds;
    int oui = 1;

    printf("[SYSTÈME] Démarrage de la Version 1 (Mode Concurrence Sauvage)\n");

    // 1. Socket LAN : Pour envoyer en Broadcast et recevoir de tous les pairs
    sock_lan = socket(AF_INET, SOCK_DGRAM, 0);
    // Permet de réutiliser l'adresse immédiatement
    setsockopt(sock_lan, SOL_SOCKET, SO_REUSEADDR, &oui, sizeof(int));
    // Active l'autorisation d'envoyer des messages de diffusion
    setsockopt(sock_lan, SOL_SOCKET, SO_BROADCAST, &oui, sizeof(int)); 

    memset(&addr_lan, 0, sizeof(addr_lan));
    addr_lan.sin_family = AF_INET;
    addr_lan.sin_port = htons(LAN_PORT);
    addr_lan.sin_addr.s_addr = INADDR_ANY; 
    bind(sock_lan, (struct sockaddr *)&addr_lan, sizeof(addr_lan));

    // 2. Socket IPC : Communication locale avec le processus Python
    sock_ipc = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&addr_ipc, 0, sizeof(addr_ipc));
    addr_ipc.sin_family = AF_INET;
    addr_ipc.sin_addr.s_addr = inet_addr("127.0.0.1");
    addr_ipc.sin_port = htons(C_PORT);
    bind(sock_ipc, (struct sockaddr *)&addr_ipc, sizeof(addr_ipc));

    // Destination : Processus Python local
    memset(&addr_py, 0, sizeof(addr_py));
    addr_py.sin_family = AF_INET;
    addr_py.sin_port = htons(PY_PORT);
    addr_py.sin_addr.s_addr = inet_addr(PY_HOST);

    // Destination : Adresse de Broadcast réseau (tout le monde)
    memset(&addr_broadcast, 0, sizeof(addr_broadcast));
    addr_broadcast.sin_family = AF_INET;
    addr_broadcast.sin_port = htons(LAN_PORT);
    addr_broadcast.sin_addr.s_addr = inet_addr("255.255.255.25s5");

    printf("--- PASSERELLE C PRÊTE (LAN:%d <-> IPC:%d) ---\n", LAN_PORT, C_PORT);

    while(1) {
        FD_ZERO(&ensemble_fds);
        FD_SET(sock_lan, &ensemble_fds);
        FD_SET(sock_ipc, &ensemble_fds);

        int max_fd = (sock_lan > sock_ipc) ? sock_lan : sock_ipc;
        
        // Surveillance des sockets pour la gestion de la concurrence
        select(max_fd + 1, &ensemble_fds, NULL, NULL, NULL);

        // --- CAS A : ENVOI (Python -> C -> Réseau Broadcast) ---
        if (FD_ISSET(sock_ipc, &ensemble_fds)) {
            int n = recvfrom(sock_ipc, tampon, BUFLEN - 1, 0, NULL, NULL);
            if (n > 0) {
                // Transmission immédiate au réseau local en mode "best-effort"
                sendto(sock_lan, tampon, n, 0, (struct sockaddr *)&addr_broadcast, sizeof(addr_broadcast));
                printf("[TX] Mise à jour de l'IA locale diffusée sur le réseau.\n");
            }
        }

        // --- CAS B : RÉCEPTION (Réseau -> C -> Python) ---
        if (FD_ISSET(sock_lan, &ensemble_fds)) {
            struct sockaddr_in addr_dist;
            socklen_t len = sizeof(addr_dist);
            // Réception de tous les messages, y compris ceux renvoyés par notre propre broadcast
            int n = recvfrom(sock_lan, tampon, BUFLEN - 1, 0, (struct sockaddr *)&addr_dist, &len);
            
            if (n > 0) {
                tampon[n] = '\0';
                // Relai direct vers Python pour traitement visuel
                sendto(sock_ipc, tampon, n, 0, (struct sockaddr *)&addr_py, sizeof(addr_py));
                
                char ip_exp[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &(addr_dist.sin_addr), ip_exp, INET_ADDRSTRLEN);
                printf("[RX] Données reçues de %s et relayées à Python.\n", ip_exp);
            }
        }
    }
    return 0;
}
