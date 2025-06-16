from socket import *
import os
import sys
import struct
import time
import select


ICMP_ECHO_REQUEST = 8  # ICMP type for echo request


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = string[count + 1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fetch the ICMP header from the IP packet (since, ICMP header starts after 20 bytes and extends 8 bytes)
        icmpHeader = recPacket[20:28]
        # unpacking in the format "bbHHh" corresponds to each of the parameter's bit size respectively.
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)

        if type == 0 and packetID == ID:  # Echo Reply (type 0)
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28 : 28+bytesInDouble])[0]
            rtt = (timeReceived - timeSent) * 1000  # conversion into milli sec
            return f"Response from {destAddr}: bytes={len(recPacket)} time={rtt:.2f}ms TTL={recPacket[8]}"

        # type 3 corresponds to the error and the given are corresponding error messages
        elif type == 3:  # Destination can't be reached
            if code == 0:
                return f"Destination Network Unreachable"
            elif code == 1:
                return f"Destination Host Unreachable"
            elif code == 2:
                return f"Destination Protocol Unreachable"
            elif code == 3:
                return f"Destination Port Unreachable"
            else:
                return f"Destination Unreachable (code {code})"


        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())

    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put it in the header
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  #Return the current process ID
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay


def ping(host, timeout=1, count=20):
    dest = gethostbyname(host)
    print(f"Pinging {dest} using Python:")
    print("")

    # Statistics variables
    min_rtt = float('inf')
    max_rtt = float('-inf')
    total_rtt = 0
    packet_loss = 0

    # Send ping requests to a server separated by approximately one second
    for i in range(count):
        delay = doOnePing(dest, timeout)
        print(delay)

        # Calculate mimimum, max, and average RTT in ms
        if "Request timed out." in delay:
            packet_loss += 1
        else:
            #print((delay.split("time=")[-1].split("ms")))
            time_value = float(delay.split("time=")[-1].split("ms")[0])
            total_rtt += time_value
            min_rtt = min(min_rtt, time_value)
            max_rtt = max(max_rtt, time_value)

        time.sleep(1)  # wait for one second between pings for let and calculations

    # Calculate statistics
    successful_pings = count - packet_loss
    if successful_pings > 0:
        avg_rtt = total_rtt / successful_pings
    else:
        avg_rtt = 0

    packet_loss_rate = (packet_loss / count) * 100

    print(f"\n--- {host} ping statistics ---")
    print(f"{count} packets transmitted, {successful_pings} received, {packet_loss_rate:.2f}% packet loss \n")
    if successful_pings > 0:
        print ("Approximate round trip times in milli-seconds:")
        print(f"Minimum : {min_rtt:.2f}ms, Maximum: {max_rtt:.2f}ms, Average {avg_rtt:.2f}ms")


if __name__ == "__main__":
    # Calling Ping function with the host name
    ping("192.168.195.217")