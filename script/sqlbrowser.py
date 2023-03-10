import argparse
import sys
import socket
from collections import OrderedDict


SQL_BROWSER_DEFAULT_PORT = 1434
BUFFER_SIZE = 4096
TIMEOUT = 4

def get_instance_info(host, instance=None, sql_browser_port=SQL_BROWSER_DEFAULT_PORT,
                    buffer_size=BUFFER_SIZE, timeout=TIMEOUT):
    """Gets Microsoft SQL Server instance information by querying the SQL Browser service.

    Args:
        host (str): Hostname or IP address of the SQL Server to query for information.
        instance (str): The name of the instance to query for information.
                        All instances are included if none.
        sql_browser_port (int): SQL Browser port number to query.
        buffer_size (int): Buffer size for the UDP request.
        timeout (int): timeout for the query.

    Returns:
        dict: A dictionary with the server name as the key and a dictionary of the
            server information as the value.

    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout
    sock.settimeout(timeout)

    server_address = (host, sql_browser_port)

    if instance:
        # The message is a CLNT_UCAST_INST packet to get a single instance
        # https://msdn.microsoft.com/en-us/library/cc219746.aspx
        message = '\x04%s\x00' % instance
        # Encode the message as a bytesarray
    else:
        # The message is a CLNT_UCAST_EX packet to get all instances
        # https://msdn.microsoft.com/en-us/library/cc219745.aspx
        message = '\x03'
        #message = '\x04\x59\x55\x4b\x4f\x4e\x53\x54\x44\x00'

    # Encode the message as a bytesarray
    message = message.encode()

    # Send data
    sock.sendto(message, server_address)

    # Receive response
    data, server = sock.recvfrom(buffer_size)

    results = []

    # Loop through the server data
    for server in data[3:].decode().split(';;'):
        server_info = OrderedDict()
        chunk = server.split(';')

        if len(chunk) > 1:
            for i in range(1, len(chunk), 2):
                server_info[chunk[i - 1]] = chunk[i]

            results.append(server_info)

    # Close socket
    sock.close()

    print(results)

    return results