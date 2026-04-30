#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/select.h>

/* --- PORTS CONFIGURATION --- */
#define PY_HOST         "127.0.0.1"
#define PY_PORT         1030    // C sends the datas to Python
#define C_PORT          1040    // Python sends the datas to C
#define LAN_PORT        4950    // Broadcast Port on LAN
#define BUFLEN          2048    // Max size of JSON messages

int main() {
    int sock_lan, sock_ipc;
    struct sockaddr_in addr_lan, addr_ipc, addr_py, addr_broadcast;
    char buffer[BUFLEN];
    fd_set fds_set;
    int yes = 1;

    // 1. Socket LAN : To Send to Broadcast and receive by everyone
    sock_lan = socket(AF_INET, SOCK_DGRAM, 0);
    // Allow immediately to reuse address 
    setsockopt(sock_lan, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int));
    // Active authorisation to send broadcast messages
    setsockopt(sock_lan, SOL_SOCKET, SO_BROADCAST, &yes, sizeof(int)); 

    memset(&addr_lan, 0, sizeof(addr_lan));
    addr_lan.sin_family = AF_INET;
    addr_lan.sin_port = htons(LAN_PORT);
    addr_lan.sin_addr.s_addr = INADDR_ANY; 
    bind(sock_lan, (struct sockaddr *)&addr_lan, sizeof(addr_lan));

    // 2. Socket IPC : Local Communication with Python Process
    sock_ipc = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&addr_ipc, 0, sizeof(addr_ipc));
    addr_ipc.sin_family = AF_INET;
    addr_ipc.sin_addr.s_addr = inet_addr("127.0.0.1");
    addr_ipc.sin_port = htons(C_PORT);
    bind(sock_ipc, (struct sockaddr *)&addr_ipc, sizeof(addr_ipc));

    // Destination : Local Python Process
    memset(&addr_py, 0, sizeof(addr_py));
    addr_py.sin_family = AF_INET;
    addr_py.sin_port = htons(PY_PORT);
    addr_py.sin_addr.s_addr = inet_addr(PY_HOST);

    // Destination : Broadcast Address (Everyone)
    memset(&addr_broadcast, 0, sizeof(addr_broadcast));
    addr_broadcast.sin_family = AF_INET;
    addr_broadcast.sin_port = htons(LAN_PORT);
    addr_broadcast.sin_addr.s_addr = inet_addr("255.255.255.255");

    while(1) {
        FD_ZERO(&fds_set);
        FD_SET(sock_lan, &fds_set);
        FD_SET(sock_ipc, &fds_set);

        int max_fd = (sock_lan > sock_ipc) ? sock_lan : sock_ipc;
        
        // Sockets Monitoring for the handling of concurrency
        select(max_fd + 1, &fds_set, NULL, NULL, NULL);

        // --- CASE A : SENDING (Python -> C -> Broadcast) ---
        if (FD_ISSET(sock_ipc, &fds_set)) {
            int n = recvfrom(sock_ipc, buffer, BUFLEN - 1, 0, NULL, NULL);
            if (n > 0) {
                // Immediate transmission to the local network on a ‘best-effort’ basis
                sendto(sock_lan, buffer, n, 0, (struct sockaddr *)&addr_broadcast, sizeof(addr_broadcast));
            }
        }

        // --- CASE B : RECEIVING (Network -> C -> Python) ---
        if (FD_ISSET(sock_lan, &fds_set)) {
            struct sockaddr_in addr_dist;
            socklen_t len = sizeof(addr_dist);
            // Receiving all messages, including those sent by our own broadcast
            int n = recvfrom(sock_lan, buffer, BUFLEN - 1, 0, (struct sockaddr *)&addr_dist, &len);
            
            if (n > 0) {
                buffer[n] = '\0';
                // Direct integration with Python for visual processing
                sendto(sock_ipc, buffer, n, 0, (struct sockaddr *)&addr_py, sizeof(addr_py));
                
                char ip_exp[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &(addr_dist.sin_addr), ip_exp, INET_ADDRSTRLEN);
            }
        }
    }
    return 0;
}
