#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/udp.h>
#include <strings.h>
#include <netdb.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <string.h>

#define BUFLEN 512

#define Py_HOST "127.0.0.1"
#define Py_PORT 1030
#define C_PORT 1040


void stop(char *s) {
        perror(s);
        exit(1);
}

int python_c_socket_send(char * ip, int port, struct sockaddr_in *dest_addr) {
    int sockfd;
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0){
        stop("ERROR opening socket");
    }

    char *host_name = ip;
    struct hostent *server;
    server = gethostbyname(host_name);
    if (server == NULL){
        stop("ERROR no such host");
    }

    bzero(dest_addr, sizeof(*dest_addr));
    // memset(dest_addr, 0, sizeof(*dest_addr));

    dest_addr->sin_family = AF_INET;
    dest_addr->sin_port = htons(port);
    bcopy(server->h_addr, &dest_addr->sin_addr.s_addr, server->h_length);
    // memcpy(&dest_addr->sin_addr.s_addr, server->h_addr, server->h_length);

    return sockfd;
}

int python_c_socket_recv(int port, struct sockaddr_in *dest_addr) {

    int sockfd;
	sockfd = socket(AF_INET, SOCK_DGRAM, 0);
	if (sockfd < 0){
		stop("ERROR opening socket");
	}

	bzero(dest_addr, sizeof(*dest_addr));
    // memset(dest_addr, 0, sizeof(*dest_addr));
	dest_addr->sin_family = AF_INET;
    dest_addr->sin_addr.s_addr = INADDR_ANY;

	dest_addr->sin_port = htons(port);

    if (bind(sockfd, (struct sockaddr *) dest_addr, sizeof(*dest_addr)) < 0) {
        stop("bind");
    }

    return sockfd;
}


int receive_data(int sock, char *data){
    int sockfd = sock;

    struct sockaddr_in src_addr;
	bzero(&src_addr, sizeof(src_addr));

    bzero(data, BUFLEN + 1);

    int len = sizeof(src_addr);
    ssize_t nbbytes;

    // recv the message
    if ( (nbbytes = recvfrom(sockfd, data, BUFLEN , 0 , (struct sockaddr *) &src_addr, (socklen_t *)&len)) < 0) {
        stop("recvfrom()"); 
    }

    printf("Recvfrom : %s\n", data);
    // printf("IP : %s, PORT : %d\n", inet_ntoa(src_addr.sin_addr), ntohs(src_addr.sin_port));

    data[nbbytes] = '\0';

    close(sockfd);
    return EXIT_SUCCESS;
}

int send_data(int sock, struct sockaddr_in *dest_addr, char *data) {

    int sockfd = sock;

    char *msg = data;
    ssize_t n = sendto(sockfd, msg, strlen(msg), 0, (struct sockaddr *)dest_addr, sizeof(*dest_addr));
    if (n < 0) {
        stop("ERROR sendto");
    }

    close(sockfd);
    return EXIT_SUCCESS;
}

int main(int argc, char *argv[]) {
    char data[BUFLEN + 1]; 
    struct sockaddr_in dest_addr;

    int sock = python_c_socket_recv(C_PORT, &dest_addr);
    receive_data(sock, data);

    int sockfd = python_c_socket_send(Py_HOST, Py_PORT, &dest_addr);
    send_data(sockfd, &dest_addr, data);

    return EXIT_SUCCESS;
}
