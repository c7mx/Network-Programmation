#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/select.h>
#include <time.h>

#define PORT_LOCAL_C    1040  // Port pour recevoir de Python
#define PORT_LOCAL_PY   1030  // Port pour envoyer vers Python
#define PORT_P2P        4950  // Port pour la communication Internet
#define BUFLEN          512

typedef struct __attribute__((packed)) {
    int uid, pv, x, y, etat;
} PaquetDonnees;

int main() {
    int sock_local, sock_remote;
    struct sockaddr_in addr_local_in, addr_local_out, addr_remote;
    char buffer[BUFLEN];
    fd_set readfds;

    // 1. Socket Local : Reçoit les données de l'IA Python
    sock_local = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&addr_local_in, 0, sizeof(addr_local_in));
    addr_local_in.sin_family = AF_INET;
    addr_local_in.sin_port = htons(PORT_LOCAL_C);
    addr_local_in.sin_addr.s_addr = INADDR_ANY;
    bind(sock_local, (struct sockaddr *)&addr_local_in, sizeof(addr_local_in));

    // Préparation de l'adresse pour renvoyer vers Python
    memset(&addr_local_out, 0, sizeof(addr_local_out));
    addr_local_out.sin_family = AF_INET;
    addr_local_out.sin_port = htons(PORT_LOCAL_PY);
    addr_local_out.sin_addr.s_addr = inet_addr("127.0.0.1");

    // 2. Socket Internet : Communique avec les autres joueurs (P2P)
    sock_remote = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&addr_remote, 0, sizeof(addr_remote));
    addr_remote.sin_family = AF_INET;
    addr_remote.sin_port = htons(PORT_P2P);
    addr_remote.sin_addr.s_addr = INADDR_ANY;
    bind(sock_remote, (struct sockaddr *)&addr_remote, sizeof(addr_remote));

    printf("La passerelle C (Internet <-> Python) est en cours d'exécution...\n");

    while(1) {
        FD_ZERO(&readfds);
        FD_SET(sock_local, &readfds);
        FD_SET(sock_remote, &readfds);

        int max_sd = (sock_local > sock_remote) ? sock_local : sock_remote;
        select(max_sd + 1, &readfds, NULL, NULL, NULL);

        // CAS 1 : Réception depuis Python -> Diffusion vers Internet
        if (FD_ISSET(sock_local, &readfds)) {
            int n = recvfrom(sock_local, buffer, BUFLEN, 0, NULL, NULL);
            printf("Données reçues de l'IA : %s. Envoi vers les pairs...\n", buffer);
            // Ici, vous devez envoyer ce message aux IPs de votre liste_machines
        }

        // CAS 2 : Réception depuis Internet -> Transmission vers l'IA Python
        if (FD_ISSET(sock_remote, &readfds)) {
            int n = recvfrom(sock_remote, buffer, BUFLEN, 0, NULL, NULL);
            printf("Données reçues d'Internet. Transmission à l'IA...\n");
            sendto(sock_local, buffer, n, 0, (struct sockaddr *)&addr_local_out, sizeof(addr_local_out));
        }
    }
    return 0;
}
