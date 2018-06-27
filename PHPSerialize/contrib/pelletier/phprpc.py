import re, md5

from twisted.protocols.basic import _PauseableMixin
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor, threads, error

import PHPSerialize, PHPUnserialize

class PHPRPC(Protocol, _PauseableMixin):

    MAX_LENGTH = 99999
    recvd = ""
    len_pattern = re.compile(r'\d+:')
    header_pattern = re.compile(r'(\d+):([\dA-Fa-f]+):')   # len:checksum:data

    def __init__(self):
        self.writer = PHPSerialize.PHPSerialize()
        self.reader = PHPUnserialize.PHPUnserialize()

    def connectionMade(self):
        #self.sendPacket("query", ("select title where 'toyota' limit 10"))
        pass

    def dropConnection(self, msg):
        self.recvd = ''
        self.sendPacket(False, msg)

    def dataReceived(self, data):
        self.recvd = self.recvd + data
        if len(self.recvd) > self.MAX_LENGTH:
            self.dropConnection('Data packet exceeded maximum length')

        g = self.len_pattern.match(self.recvd)
        if not g and self.recvd.find(':'):
            self.dropConnection('invalid start of packet')
            
        g = self.header_pattern.match(self.recvd)

        if g:
            g = g.groups()

            while g and not self.paused:        
                s = g[0]
                length = int(s)
                digest = g[1]
                header_length = len(s) + len(digest) + 2

                if len(self.recvd) < length + header_length: # not enough data
                    break

                packet = self.recvd[header_length:length+header_length]
                self.recvd = self.recvd[length+header_length:]
                if digest != md5.md5(packet).hexdigest():
                    self.dropConnection('Checksum error.')
                else:
                    try:
                        data = self.reader.unserialize(packet)
                    except:
                        self.dropConnection('Cound not unserialize %s')

                    self.packetReceived(data)
                    self.recvd = ''

    def packetReceived(self, data):
        """
        This method is called when a complete packet is received.
        It expects its first argument to be a 2-tuple in the form of
        (name, args).  The code looks for a method called
        phprpc_<name> and calls it, applying the given arguments.


        Writes back to the client a 2-tuple in the form of (code,
        result).  If code is True, then result is the result of the
        method.  if code is False, then result is an error string
        describing the error that occurred.
        """

        name = data[0]

        # PHP does not have a "list", ordered arrays are turned into
        # Python distionaries with integer keys, so the dictionary
        # must be unpacked to get the arguments
        args = [data[1][i] for i in range(len(data[1]))]
        meth = getattr(self, 'phprpc_' + name, None)
        if meth is None:
            self.sendPacket(False, "No such method %s" % name)
        else:
            self.sendPacket(True, apply(meth, args))
            self.connected = 0

    def sendPacket(self, success, data):
        """
        This method encodes and sends data to the client.  The packet
        format is:

        len:checksum:data

        When len is an integer string, checksum is a 32-char
        md5.hexdigest of the data, and data is the literal encoded
        data.
        """
        data = self.writer.serialize((success, data))
        self.transport.write('%s:%s:%s' % (len(data), md5.md5(data).hexdigest(), data))

    def phprpc_echo(self, *args):
        return args

if __name__ == '__main__':
    factory = Factory()
    factory.protocol = PHPRPC

    reactor.listenTCP(8007, factory)
    reactor.run()
    

