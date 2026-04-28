#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/select.h>
#include <errno.h>
#include <signal.h>

/* --- CONFIGURATION --- */
#define PY_HOST         "127.0.0.1"
#define PY_PORT         1030    
#define C_PORT          1040    
#define LAN_PORT        4950    
#define BUFLEN          4096    

/* Fonction utilitaire pour vérifier la validité d'une adresse IP */
int est_ip_valide(const char *ip) {
    struct sockaddr_in sa;
    return inet_pton(AF_INET, ip, &(sa.sin_addr)) != 0;
}

int main() {
    int sock_lan, sock_ipc;
    struct sockaddr_in addr_lan, addr_ipc, addr_py, addr_broadcast;
    char tampon[BUFLEN];
    char tampon_envoi[BUFLEN + 64]; 
    fd_set ensemble_fds;
    int oui = 1;

    // Ignorer le signal SIGPIPE pour éviter le crash si une socket est fermée
    signal(SIGPIPE, SIG_IGN);

    // 1. Configuration de la Socket LAN
    if ((sock_lan = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        fprintf(stderr, "[ERREUR] Impossible de créer la socket LAN : %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    if (setsockopt(sock_lan, SOL_SOCKET, SO_REUSEADDR, &oui, sizeof(int)) < 0) {
        fprintf(stderr, "[ALERTE] Échec de SO_REUSEADDR : %s\n", strerror(errno));
    }

    if (setsockopt(sock_lan, SOL_SOCKET, SO_BROADCAST, &oui, sizeof(int)) < 0) {
        fprintf(stderr, "[ERREUR] Impossible d'activer le mode Broadcast : %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    memset(&addr_lan, 0, sizeof(addr_lan));
    addr_lan.sin_family = AF_INET;
    addr_lan.sin_port = htons(LAN_PORT);
    addr_lan.sin_addr.s_addr = INADDR_ANY; 
    
    if (bind(sock_lan, (struct sockaddr *)&addr_lan, sizeof(addr_lan)) < 0) {
        fprintf(stderr, "[ERREUR] Échec du bind LAN (Port %d) : %s. Le port est peut-être déjà utilisé.\n", LAN_PORT, strerror(errno));
        close(sock_lan);
        exit(EXIT_FAILURE);
    }

    // 2. Configuration de la Socket IPC (Communication Inter-Processus avec Python)
    if ((sock_ipc = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        fprintf(stderr, "[ERREUR] Impossible de créer la socket IPC : %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    memset(&addr_ipc, 0, sizeof(addr_ipc));
    addr_ipc.sin_family = AF_INET;
    addr_ipc.sin_addr.s_addr = inet_addr("127.0.0.1");
    addr_ipc.sin_port = htons(C_PORT);
    
    if (bind(sock_ipc, (struct sockaddr *)&addr_ipc, sizeof(addr_ipc)) < 0) {
        fprintf(stderr, "[ERREUR] Échec du bind IPC (Port %d) : %s\n", C_PORT, strerror(errno));
        close(sock_ipc);
        exit(EXIT_FAILURE);
    }

    // Préparation des adresses de destination
    memset(&addr_py, 0, sizeof(addr_py));
    addr_py.sin_family = AF_INET;
    addr_py.sin_port = htons(PY_PORT);
    addr_py.sin_addr.s_addr = inet_addr(PY_HOST);

    memset(&addr_broadcast, 0, sizeof(addr_broadcast));
    addr_broadcast.sin_family = AF_INET;
    addr_broadcast.sin_port = htons(LAN_PORT);
    addr_broadcast.sin_addr.s_addr = inet_addr("255.255.255.255");

    printf("[RESEAU C] Système prêt. Mode : P2P Multi-Participants.\n");

    while(1) {
        FD_ZERO(&ensemble_fds);
        FD_SET(sock_lan, &ensemble_fds);
        FD_SET(sock_ipc, &ensemble_fds);

        int max_fd = (sock_lan > sock_ipc) ? sock_lan : sock_ipc;
        
        if (select(max_fd + 1, &ensemble_fds, NULL, NULL, NULL) < 0) {
            if (errno == EINTR) continue; // Ignorer si interrompu par un signal
            perror("[ERREUR] Échec de la fonction select");
            break;
        }

        // --- ENVOI : Python -> LAN ---
        if (FD_ISSET(sock_ipc, &ensemble_fds)) {
            int n = recvfrom(sock_ipc, tampon, BUFLEN - 1, 0, NULL, NULL);
            if (n < 0) {
                fprintf(stderr, "[ALERTE] Erreur de réception depuis Python : %s\n", strerror(errno));
                continue;
            }
            tampon[n] = '\0';
            
            // Gestion de l'Unicast
            if (strncmp(tampon, "IP:", 3) == 0) {
                char *separateur = strchr(tampon, '|');
                if (separateur) {
                    *separateur = '\0';
                    char *ip_dest = tampon + 3;
                    char *contenu = separateur + 1;

                    if (est_ip_valide(ip_dest)) {
                        struct sockaddr_in addr_uni;
                        memset(&addr_uni, 0, sizeof(addr_uni));
                        addr_uni.sin_family = AF_INET;
                        addr_uni.sin_port = htons(LAN_PORT);
                        addr_uni.sin_addr.s_addr = inet_addr(ip_dest);

                        if (sendto(sock_lan, contenu, strlen(contenu), 0, (struct sockaddr *)&addr_uni, sizeof(addr_uni)) < 0) {
                            fprintf(stderr, "[ERREUR] Échec de l'Unicast vers %s : %s\n", ip_dest, strerror(errno));
                        }
                    } else {
                        fprintf(stderr, "[ALERTE] IP de destination invalide : %s\n", ip_dest);
                    }
                }
            } else {
                // Envoi en Broadcast (Mode par défaut)
                if (sendto(sock_lan, tampon, n, 0, (struct sockaddr *)&addr_broadcast, sizeof(addr_broadcast)) < 0) {
                    fprintf(stderr, "[ERREUR] Échec du Broadcast : %s\n", strerror(errno));
                }
            }
        }

        // --- RÉCEPTION : LAN -> Python ---
        if (FD_ISSET(sock_lan, &ensemble_fds)) {
            struct sockaddr_in addr_expediteur;
            socklen_t len = sizeof(addr_expediteur);
            int n = recvfrom(sock_lan, tampon, BUFLEN - 1, 0, (struct sockaddr *)&addr_expediteur, &len);
            
            if (n > 0) {
                tampon[n] = '\0';
                char ip_source[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &(addr_expediteur.sin_addr), ip_source, INET_ADDRSTRLEN);

                // Découverte Passive : On ajoute l'IP source pour que Python identifie l'expéditeur
                int resultat = snprintf(tampon_envoi, sizeof(tampon_envoi), "%s|%s", ip_source, tampon);
                if (resultat >= (int)sizeof(tampon_envoi)) {
                    fprintf(stderr, "[ALERTE] Paquet trop volumineux, données tronquées.\n");
                }
                
                if (sendto(sock_ipc, tampon_envoi, strlen(tampon_envoi), 0, (struct sockaddr *)&addr_py, sizeof(addr_py)) < 0) {
                    fprintf(stderr, "[ERREUR] Impossible de transmettre les données à Python : %s\n", strerror(errno));
                }
            } else if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
                fprintf(stderr, "[ERREUR] Échec de recvfrom LAN : %s\n", strerror(errno));
            }
        }
    }

    close(sock_lan);
    close(sock_ipc);
    return 0;
}
