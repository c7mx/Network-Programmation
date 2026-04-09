#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/select.h>
#include <time.h>

/* --- CONFIGURATION DES PORTS ET TIMEOUTS --- */
#define PY_HOST         "127.0.0.1"
#define PY_PORT         1030    // C envoie vers Python ici
#define C_PORT          1040    // C écoute Python ici
#define LAN_PORT        4950    // Port de communication P2P entre joueurs
#define BUFLEN          1024    // Taille augmentée pour les chaînes JSON

#define MSG_ANNONCE     "ANNONCE"
#define INTERVALLE_ANN  5       // Fréquence d'annonce (secondes)
#define TIMEOUT_MACHINE 15      // Temps avant de supprimer un pair
#define MAX_PAIRS       20

typedef struct {
    char ip[INET_ADDRSTRLEN];
    time_t derniere_activite;
} MachinePair;

/* --- VARIABLES GLOBALES --- */
MachinePair liste_machines[MAX_PAIRS];
int nb_machines = 0;
char mon_ip_reelle[INET_ADDRSTRLEN];

/* --- FONCTIONS DE GESTION DU RÉSEAU --- */

// Nettoie các pairs inactifs (Gestion de la présence)
void nettoyer_liste_machines() {
    time_t maintenant = time(NULL);
    for (int i = 0; i < nb_machines; i++) {
        if (maintenant - liste_machines[i].derniere_activite > TIMEOUT_MACHINE) {
            printf("[SYSTÈME] Pair déconnecté : %s\n", liste_machines[i].ip);
            for (int j = i; j < nb_machines - 1; j++) {
                liste_machines[j] = liste_machines[j+1];
            }
            nb_machines--; 
            i--;
        }
    }
}

// Détecte l'IP LAN pour éviter de traiter ses propres messages
void detecter_mon_ip_lan() {
    int s = socket(AF_INET, SOCK_DGRAM, 0);
    struct sockaddr_in serv;
    memset(&serv, 0, sizeof(serv));
    serv.sin_family = AF_INET;
    serv.sin_addr.s_addr = inet_addr("8.8.8.8");
    serv.sin_port = htons(53);
    connect(s, (const struct sockaddr*)&serv, sizeof(serv));
    struct sockaddr_in name;
    socklen_t namelen = sizeof(name);
    getsockname(s, (struct sockaddr*)&name, &namelen);
    inet_ntop(AF_INET, &name.sin_addr, mon_ip_reelle, INET_ADDRSTRLEN);
    close(s);
}

// Mise à jour de la liste des pairs (P2P sans serveur)
void mettre_a_jour_liste(char *ip_recu) {
    if (strcmp(ip_recu, mon_ip_reelle) == 0) return; 
    for (int i = 0; i < nb_machines; i++) {
        if (strcmp(liste_machines[i].ip, ip_recu) == 0) {
            liste_machines[i].derniere_activite = time(NULL);
            return;
        }
    }
    if (nb_machines < MAX_PAIRS) {
        strcpy(liste_machines[nb_machines].ip, ip_recu);
        liste_machines[nb_machines].derniere_activite = time(NULL);
        nb_machines++;
        printf("[RÉSEAU] Nouveau pair détecté : %s\n", ip_recu);
    }
}

/* --- PROGRAMME PRINCIPAL --- */

int main() {
    int sock_lan, sock_ipc;
    struct sockaddr_in addr_lan, addr_ipc, addr_py, addr_broadcast;
    char tampon[BUFLEN];
    fd_set ensemble_fds;
    struct timeval delai;
    int oui = 1;

    detecter_mon_ip_lan();
    printf("[INFO] Passerelle réseau démarrée sur l'IP : %s\n", mon_ip_reelle);

    // 1. Socket LAN (Communication P2P externe)
    sock_lan = socket(AF_INET, SOCK_DGRAM, 0);
    setsockopt(sock_lan, SOL_SOCKET, SO_REUSEADDR, &oui, sizeof(int));
    setsockopt(sock_lan, SOL_SOCKET, SO_BROADCAST, &oui, sizeof(int));
    memset(&addr_lan, 0, sizeof(addr_lan));
    addr_lan.sin_family = AF_INET;
    addr_lan.sin_port = htons(LAN_PORT);
    addr_lan.sin_addr.s_addr = INADDR_ANY;
    bind(sock_lan, (struct sockaddr *)&addr_lan, sizeof(addr_lan));

    // 2. Socket IPC (Communication locale avec Python)
    sock_ipc = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&addr_ipc, 0, sizeof(addr_ipc));
    addr_ipc.sin_family = AF_INET;
    addr_ipc.sin_addr.s_addr = inet_addr("127.0.0.1");
    addr_ipc.sin_port = htons(C_PORT);
    bind(sock_ipc, (struct sockaddr *)&addr_ipc, sizeof(addr_ipc));

    // Destination Python
    memset(&addr_py, 0, sizeof(addr_py));
    addr_py.sin_family = AF_INET;
    addr_py.sin_port = htons(PY_PORT);
    addr_py.sin_addr.s_addr = inet_addr(PY_HOST);

    // Adresse de Broadcast
    memset(&addr_broadcast, 0, sizeof(addr_broadcast));
    addr_broadcast.sin_family = AF_INET;
    addr_broadcast.sin_port = htons(LAN_PORT);
    addr_broadcast.sin_addr.s_addr = inet_addr("255.255.255.255");

    printf("--- PASSERELLE C PRÊTE (LAN:%d, IPC:%d) ---\n", LAN_PORT, C_PORT);

    while(1) {
        FD_ZERO(&ensemble_fds);
        FD_SET(sock_lan, &ensemble_fds);
        FD_SET(sock_ipc, &ensemble_fds);

        int max_fd = (sock_lan > sock_ipc) ? sock_lan : sock_ipc;
        delai.tv_sec = INTERVALLE_ANN;
        delai.tv_usec = 0;

        // select() gère la concurrence entre IA locale et adversaires distants
        int activite = select(max_fd + 1, &ensemble_fds, NULL, NULL, &delai);

        // --- CAS 1 : L'IA LOCALE AGIT (Python -> LAN) ---
        if (activite > 0 && FD_ISSET(sock_ipc, &ensemble_fds)) {
            int n = recvfrom(sock_ipc, tampon, BUFLEN - 1, 0, NULL, NULL);
            if (n > 0) {
                tampon[n] = '\0'; // Sécurité pour la chaîne de caractères
                for (int i = 0; i < nb_machines; i++) {
                    struct sockaddr_in dest;
                    dest.sin_family = AF_INET;
                    dest.sin_port = htons(LAN_PORT);
                    dest.sin_addr.s_addr = inet_addr(liste_machines[i].ip);
                    sendto(sock_lan, tampon, n, 0, (struct sockaddr *)&dest, sizeof(dest));
                }
                printf("[TO LAN] JSON local relayé vers le réseau.\n");
            }
        }

        // --- CAS 2 : UN ADVERSAIRE AGIT (LAN -> Python) ---
        else if (activite > 0 && FD_ISSET(sock_lan, &ensemble_fds)) {
            struct sockaddr_in addr_dist;
            socklen_t len = sizeof(addr_dist);
            int n = recvfrom(sock_lan, tampon, BUFLEN - 1, 0, (struct sockaddr *)&addr_dist, &len);
            
            if (n > 0) {
                char ip_exp[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &(addr_dist.sin_addr), ip_exp, INET_ADDRSTRLEN);

                if (n >= 7 && strncmp(tampon, MSG_ANNONCE, 7) == 0) {
                    mettre_a_jour_liste(ip_exp);
                } else {
                    tampon[n] = '\0'; // Important pour le décodage Python
                    sendto(sock_ipc, tampon, n, 0, (struct sockaddr *)&addr_py, sizeof(addr_py));
                    printf("[P2P] Données reçues de %s -> Python.\n", ip_exp);
                }
            }
        }

        // --- CAS 3 : ANNONCE ET MAINTENANCE ---
        else if (activite == 0) {
            nettoyer_liste_machines(); // Suppression des pairs inactifs
            sendto(sock_lan, MSG_ANNONCE, strlen(MSG_ANNONCE), 0, 
                   (struct sockaddr *)&addr_broadcast, sizeof(addr_broadcast));
        }
    }
    return 0;
}
