
import socket,os,struct,time,sys

if sys.version_info[0] < 3:
    import thread
else:
    import _thread as thread
class mySockets:
    def __init__(self, type = 'file', proto = 'packed'):
        self.socketType = type
        self.client_handler = self.handle
        # Proto: "simple" or "packed". 
        # Simple accept plain text but only 1024 chars (for simple clients)
        # Packed packs data with struct.pack and send it as binary 
        self.proto = proto 

    def client_send(self, data):
        self.send(data)
        data = self.read()
        self.close()
        return data

    def send(self, obj, connection = None):
        msg = obj.encode()
        #print(msg)
        if self.proto == "simple":
            connection.send(msg)
        else:
            if self.socket:
                frmt = "=%ds" % len(msg)
                packed_msg = struct.pack(frmt, msg)
                packed_hdr = struct.pack('!I', len(packed_msg))

                self._send(packed_hdr, connection)
                self._send(packed_msg, connection)
    def _send(self, msg, connection = None):
        if not connection:
            connection = self.socket
        sent = 0
        while sent < len(msg):
            sent += connection.send(msg[sent:])


    def _read(self, connection, size):
        data = b''
        while len(data) < size:
            data_tmp = connection.recv(size-len(data))
            data = b''.join([data, data_tmp])
            #data += data_tmp
            if data_tmp == '':
                #print size
                #break
                raise RuntimeError("socket connection broken")
        return data

    def read(self, connection = None):
        if not connection:
            connection = self.socket
        
        if self.proto == 'simple':
            data = connection.recv(1024)
            return data
        else:
            size = self._msg_length(connection)
            data = self._read(connection,size)
            if (data):
                frmt = "=%ds" % size
                msg = struct.unpack(frmt, data)
                return msg[0]
            else:
                return ''

    def _msg_length(self, connection):
        d = self._read(connection, 4)
        s = struct.unpack('!I', d)
        return s[0]

    def server(self, file, perm = 0o666):
        if self.socketType == 'file':
            try:
                os.remove(file)
            except OSError:
                pass
        self.socket = socket.socket(socket.AF_UNIX if self.socketType == 'file' else  socket.AF_INET, socket.SOCK_STREAM)
        if self.socketType != 'file':
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(file)
        self.socket.listen(5)
        if self.socketType == 'file':
            os.chmod(file, perm)
        #s = socket.socket()
        #host = socket.gethostname() # Get local machine name
        #port = 50000                # Reserve a port for your service.
        #s.bind((host, port))

    def on_message(self, func):
        self.client_handler = func

    def client(self, file):
        self.socket = socket.socket(socket.AF_UNIX if self.socketType == 'file' else  socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(file)

    def close(self):
        self.socket.close()

    def handle_client(self, connection, addr):
        data = self.read(connection)
        self.send(self.client_handler(data.decode('utf-8')), connection)
        connection.close()

    def serve(self):
        conn, addr = self.socket.accept()
        thread.start_new_thread(self.handle_client,(conn,addr))

    def handle(self, data):
        return data
