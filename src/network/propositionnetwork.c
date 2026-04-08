#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/socket.h>

#define PORT_C 1040
#define BUFLEN 1024

void stop(char *s) {
    perror(s);
    exit(EXIT_FAILURE);
}

int main(void) {
    int sockfd, nbbytes;
    struct sockaddr_in addr_c, addr_python;
    socklen_t len;
    char buffer[BUFLEN];

    // Création socket UDP
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1)
        stop("socket");

    // Configuration de C (écoute)
    memset(&addr_c, 0, sizeof(addr_c));
    addr_c.sin_family = AF_INET;
    addr_c.sin_port = htons(PORT_C);
    addr_c.sin_addr.s_addr = INADDR_ANY;

    if (bind(sockfd, (struct sockaddr *)&addr_c, sizeof(addr_c)) < 0)
        stop("bind failed");

    printf("Serveur C prêt sur le port %d...\n", PORT_C);

    while (1) {
        len = sizeof(addr_python);

        // recevoir msg
        if ((nbbytes = recvfrom(sockfd, buffer, BUFLEN, 0,
                                (struct sockaddr *)&addr_python, &len)) < 0)
            stop("recvfrom()");

        // Extraire entier envoyé en network byte order
        uint32_t number;
        memcpy(&number, buffer, sizeof(uint32_t));
        number = ntohl(number);

        // Extraire chaîne après l'entier
        char message[BUFLEN];
        strncpy(message, buffer + sizeof(uint32_t), nbbytes - sizeof(uint32_t));
        message[nbbytes - sizeof(uint32_t)] = '\0';

        printf("Reçu: '%s' avec entier: %u\n", message, number);

        // Préparer réponse : "PONG" + nombre + 1
        const char *resp_str = "PONG";
        uint32_t resp_num = htonl(number + 1);
        char resp_buf[BUFLEN];
        memcpy(resp_buf, &resp_num, sizeof(uint32_t));
        strcpy(resp_buf + sizeof(uint32_t), resp_str);

        if (sendto(sockfd, resp_buf, sizeof(uint32_t) + strlen(resp_str), 0,
                   (struct sockaddr *)&addr_python, len) == -1)
            stop("sendto()");
    }

    close(sockfd);
    return 0;
}
