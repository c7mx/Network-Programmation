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

#define Py_PORT 1030
#define C_PORT 1040
#define HOST "127.0.0.1"

void stop(char *s) {
        perror(s);
        exit(1);
}

int python_c_socket_send(char * ip, int port, struct sockaddr_in *serv_addr) {
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

    bzero(serv_addr, sizeof(*serv_addr));
    // memset(serv_addr, 0, sizeof(*serv_addr));

    serv_addr->sin_family = AF_INET;
    serv_addr->sin_port = htons(port);
    bcopy(server->h_addr, &serv_addr->sin_addr.s_addr, server->h_length);
    // memcpy(&serv_addr->sin_addr.s_addr, server->h_addr, server->h_length);

    return sockfd;
}

int python_c_socket_recv(int port, struct sockaddr_in *serv_addr) {

    int sockfd;
	sockfd = socket(AF_INET, SOCK_DGRAM, 0);
	if (sockfd < 0){
		stop("ERROR opening socket");
	}

	bzero(serv_addr, sizeof(*serv_addr));
    // memset(serv_addr, 0, sizeof(*serv_addr));
	serv_addr->sin_family = AF_INET;
    serv_addr->sin_addr.s_addr = INADDR_ANY;

	serv_addr->sin_port = htons(port);

    if (bind(sockfd, (struct sockaddr *) serv_addr, sizeof(*serv_addr)) < 0) {
        stop("bind");
    }

    return sockfd;
}


int receive_data(int sock, char *data){
    int sockfd = sock;

    struct sockaddr_in cliaddr;
	bzero(&cliaddr, sizeof(cliaddr));

    bzero(data, BUFLEN + 1);

    int len = sizeof(cliaddr);
    ssize_t nbbytes;

    // recv the message
    if ( (nbbytes = recvfrom(sockfd, data, BUFLEN , 0 , (struct sockaddr *) &cliaddr, (socklen_t *)&len)) < 0) {
        stop("recvfrom()"); 
    }

    printf("Recvfrom : %s\n", data);
    // printf("IP : %s, PORT : %d\n", inet_ntoa(cliaddr.sin_addr), ntohs(cliaddr.sin_port));

    data[nbbytes] = '\0';

    close(sockfd);
    return EXIT_SUCCESS;
}

int send_data(int sock, struct sockaddr_in *serv_addr, char *data) {

    int sockfd = sock;

    char *msg = data;
    ssize_t n = sendto(sockfd, msg, strlen(msg), 0, (struct sockaddr *)serv_addr, sizeof(*serv_addr));
    if (n < 0) {
        stop("ERROR sendto");
    }

    close(sockfd);
    return EXIT_SUCCESS;
}

int main(int argc, char *argv[]) {
    char data[BUFLEN + 1];
    struct sockaddr_in serv_addr;
    
    int sock = python_c_socket_recv(C_PORT, &serv_addr);
    receive_data(sock, data);

    int sockfd = python_c_socket_send(HOST, Py_PORT, &serv_addr);
    send_data(sockfd, &serv_addr, data);

    return EXIT_SUCCESS;
}
