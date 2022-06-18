/* Sockets Example
 * Copyright (c) 2016-2020 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "mbed.h"
#include "wifi_helper.h"
#include "mbed-trace/mbed_trace.h"

// Sensors drivers present in the BSP library
#include "stm32l475e_iot01_tsensor.h"
#include "stm32l475e_iot01_hsensor.h"
#include "stm32l475e_iot01_psensor.h"
#include "stm32l475e_iot01_magneto.h"
#include "stm32l475e_iot01_gyro.h"
#include "stm32l475e_iot01_accelero.h"
#include <cstdint>
#include <cstdio>
#include <stdio.h>
#if MBED_CONF_APP_USE_TLS_SOCKET
#include "root_ca_cert.h"

#ifndef DEVICE_TRNG
#error "mbed-os-example-tls-socket requires a device which supports TRNG"
#endif
#endif // MBED_CONF_APP_USE_TLS_SOCKET





class KalmanFilter {
  private:
      float P, K, xhat, Q, R;  
  public:
    KalmanFilter();
    KalmanFilter(float _Q, float _R);
    float update(float obs);
  
};
KalmanFilter::KalmanFilter(){
    P = 0.0;   // Convariance Matrix 
    K = 0.0;   // Kalman Gain
    xhat = 0.0;// Initial Predicted Value
    Q = 0.1;  // Error     
    R = 1;
  }
  
  // override
KalmanFilter::KalmanFilter(float _Q, float _R){
    P = 0.0;   // Convariance Matrix 
    K = 0.0;   // Kalman Gain
    xhat = 0.0;// Initial Predicted Value
    Q = _Q;    // Error     
    R = _R;
  }
  
float KalmanFilter::update(float obs){
    // Predict
    float xhat_m = xhat ;   // xhat[k-1]
    float P_m    = P + Q;   // P[k-1]
  
    // Update
    float S = P_m + R;      // Remained Error
    K = P_m / S;            // Update Kalman Gain
    xhat = xhat_m + K * (obs - xhat_m); // predicted value
    P = (1 - K) * P_m;      // Convariance Matrix of Error BTW True Value and Predicted True Value 
  
    return xhat;
}
 
//define the mpu9250 object
KalmanFilter *kf[3];

 
void init(void){
    
    for(int i=0; i<3; i++)     
        kf[i] = new KalmanFilter(1e-3, 0.001);
}










class SocketDemo {
    static constexpr size_t MAX_NUMBER_OF_ACCESS_POINTS = 10;
    static constexpr size_t MAX_MESSAGE_RECEIVED_LENGTH = 100;

#if MBED_CONF_APP_USE_TLS_SOCKET
    static constexpr size_t REMOTE_PORT = 443; // tls port
#else
    static constexpr size_t REMOTE_PORT = 80; // standard HTTP port
#endif // MBED_CONF_APP_USE_TLS_SOCKET

public:
    SocketDemo() : _net(NetworkInterface::get_default_instance())
    {
    }

    ~SocketDemo()
    {
        if (_net) {
            _net->disconnect();
        }
    }
    
    void run()
    {
        if (!_net) {
            printf("Error! No network interface found.\r\n");
            return;
        }

        /* if we're using a wifi interface run a quick scan */
        if (_net->wifiInterface()) {
            /* the scan is not required to connect and only serves to show visible access points */
            wifi_scan();

            /* in this example we use credentials configured at compile time which are used by
             * NetworkInterface::connect() but it's possible to do this at runtime by using the
             * WiFiInterface::connect() which takes these parameters as arguments */
        }

        /* connect will perform the action appropriate to the interface type to connect to the network */

        printf("Connecting to the network...\r\n");

        nsapi_size_or_error_t result = _net->connect();
        if (result != 0) {
            printf("Error! _net->connect() returned: %d\r\n", result);
            return;
        }

        print_network_info();

        /* opening the socket only allocates resources */
        result = _socket.open(_net);
        if (result != 0) {
            printf("Error! _socket.open() returned: %d\r\n", result);
            return;
        }

#if MBED_CONF_APP_USE_TLS_SOCKET
        result = _socket.set_root_ca_cert(root_ca_cert);
        if (result != NSAPI_ERROR_OK) {
            printf("Error: _socket.set_root_ca_cert() returned %d\n", result);
            return;
        }
        _socket.set_hostname("192.168.198.210");//MBED_CONF_APP_HOSTNAME);
#endif // MBED_CONF_APP_USE_TLS_SOCKET

        /* now we have to find where to connect */

        SocketAddress address;

        if (!resolve_hostname(address)) {
            return;
        }

        address.set_port(REMOTE_PORT);

        /* we are connected to the network but since we're using a connection oriented
         * protocol we still need to open a connection on the socket */

        printf("Opening connection to remote port %d\r\n", REMOTE_PORT);
    
        result = _socket.connect(address);
        printf("hi");
        if (result != 0) {
            printf("Error! _socket.connect() returned: %d\r\n", result);
            return;
        }
        int sample_num=0;
        while(true){
            ++sample_num;
            printf("\nreading and sending data\n");
            
            int16_t pAccelDataXYZ[3] = {0};
            char acc_json[50];
            
            
            BSP_ACCELERO_AccGetXYZ(pAccelDataXYZ);
            int len = sprintf(acc_json,"{\"x\":%10.3f,\"y\":%10.3f,\"z\":%10.3f}",kf[0]->update(pAccelDataXYZ[0]/100),
                   kf[1]->update(pAccelDataXYZ[1]/100),
                   kf[2]->update(pAccelDataXYZ[2]/100));
            int response = _socket.send(acc_json,len);
            if (0 < response){
                printf("Error sending: %d\n", response);
            }
            ThisThread::sleep_for(50);
        }
        /*if (!send_http_request()) {
            return;
        }
        if (!receive_http_response()) {
            return;
        }*/

        printf("Demo concluded successfully \r\n");
    }

private:
    bool resolve_hostname(SocketAddress &address)
    {
        const char hostname[] = "192.168.247.86";//MBED_CONF_APP_HOSTNAME;

        /* get the host address */
        printf("\nResolve hostname %s\r\n", hostname);
        nsapi_size_or_error_t result = _net->gethostbyname(hostname, &address);
        if (result != 0) {
            printf("Error! gethostbyname(%s) returned: %d\r\n", hostname, result);
            return false;
        }

        printf("%s address is %s\r\n", hostname, (address.get_ip_address() ? address.get_ip_address() : "None") );

        return true;
    }

    bool send_http_request(char *buffer)
    {

    
        /* loop until whole request sent */
        /*const char buffer[] = "GET / HTTP/1.1\r\n"
                              "Host: 192.168.1.34\r\n"
                              "Connection: close\r\n"
                              "\r\n";*/

        nsapi_size_t bytes_to_send = strlen(buffer);
        nsapi_size_or_error_t bytes_sent = 0;

        //printf("\r\nSending message: \r\n%s", buffer);

        while (bytes_to_send) {
            bytes_sent = _socket.send(buffer + bytes_sent, bytes_to_send);
            if (bytes_sent < 0) {
                printf("Error! _socket.send() returned: %d\r\n", bytes_sent);
                return false;
            } else {
                printf("sent %d bytes\r\n", bytes_sent);
            }

            bytes_to_send -= bytes_sent;
        }

        printf("Complete message sent\r\n");

        return true;
    }

    bool receive_http_response()
    {
        char buffer[MAX_MESSAGE_RECEIVED_LENGTH];
        int remaining_bytes = MAX_MESSAGE_RECEIVED_LENGTH;
        int received_bytes = 0;

        /* loop until there is nothing received or we've ran out of buffer space */
        nsapi_size_or_error_t result = remaining_bytes;
        while (result > 0 && remaining_bytes > 0) {
            result = _socket.recv(buffer + received_bytes, remaining_bytes);
            if (result < 0) {
                printf("Error! _socket.recv() returned: %d\r\n", result);
                return false;
            }

            received_bytes += result;
            remaining_bytes -= result;
        }

        /* the message is likely larger but we only want the HTTP response code */

        printf("received %d bytes:\r\n%.*s\r\n\r\n", received_bytes, strstr(buffer, "\n") - buffer, buffer);

        return true;
    }

    void wifi_scan()
    {
        WiFiInterface *wifi = _net->wifiInterface();

        WiFiAccessPoint ap[MAX_NUMBER_OF_ACCESS_POINTS];

        /* scan call returns number of access points found */
        int result = wifi->scan(ap, MAX_NUMBER_OF_ACCESS_POINTS);

        if (result <= 0) {
            printf("WiFiInterface::scan() failed with return value: %d\r\n", result);
            return;
        }

        printf("%d networks available:\r\n", result);

        for (int i = 0; i < result; i++) {
            printf("Network: %s secured: %s BSSID: %hhX:%hhX:%hhX:%hhx:%hhx:%hhx RSSI: %hhd Ch: %hhd\r\n",
                   ap[i].get_ssid(), get_security_string(ap[i].get_security()),
                   ap[i].get_bssid()[0], ap[i].get_bssid()[1], ap[i].get_bssid()[2],
                   ap[i].get_bssid()[3], ap[i].get_bssid()[4], ap[i].get_bssid()[5],
                   ap[i].get_rssi(), ap[i].get_channel());
        }
        printf("\r\n");
    }

    void print_network_info()
    {
        /* print the network info */
        SocketAddress a;
        _net->get_ip_address(&a);
        printf("IP address: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
        _net->get_netmask(&a);
        printf("Netmask: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
        _net->get_gateway(&a);
        printf("Gateway: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
    }

private:
    NetworkInterface *_net;

#if MBED_CONF_APP_USE_TLS_SOCKET
    TLSSocket _socket;
#else
    TCPSocket _socket;
#endif // MBED_CONF_APP_USE_TLS_SOCKET
};

int main() {

    printf("Start sensor init\n");
    
    BSP_MAGNETO_Init();
    BSP_GYRO_Init();
    BSP_ACCELERO_Init();

    printf("\r\nStarting socket demo\r\n\r\n");

#ifdef MBED_CONF_MBED_TRACE_ENABLE
    mbed_trace_init();
#endif
    init();
    SocketDemo *example = new SocketDemo();
    MBED_ASSERT(example);
    example->run();
    
    return 0;
}
