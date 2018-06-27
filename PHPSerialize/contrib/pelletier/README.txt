Michel Pelletier (pelletier.michel@gmail.com)

Attached are two files, the Twisted server and the PHP client.  
The server class is registered with the Twisted "reactor" and 
new instances are created when connections are made to the server.  
Each instance holds one connection.  When data is received from the 
connection, the "dataReceived" method of the class is "fired".  
This is the main "event" when they talk of Twisted being an event 
driven framework.

The data chunk is accumulated until the header regular expression 
matches, then the packet is disassembled.  Some rudementary length 
checking is done, and the "payload" is checked against the transmited 
md5 hexdigest to ensure data integrity (a customer requirement, I'm 
not entirely certain it's necessary but it must remain for now).  
The payload is then unserialized using your library.  

The data payload must consist of an array of two elements, the first 
element being the name of the RPC method to call, and the remaining 
argumenting being an array of arguments to call on that method.  
The name is looked up in the class as 'phprpc_<name>' for example, 
the method phprpc_echo() is implemented in the class I am sending 
you which simply returns the exact same arguments that are sent to it.  
Subclasses would extend this class with their own 'phprpc_<name>' 
methods that are "remote" methods that can be invoked by the client.  
This pattern exactly mimics the existing Twisted xmlrpc server.

The looked up method is then invoked (or an error happens, error 
handling isn't great ATM) and the result is serialized and send back to 
the client.  The client unserializes the data returns the result to the 
PHP script.  A PHP system can persistently hold onto a connection and 
issue many RPC requests for efficiency although this is not rigorously 
tested.

Drop me a line if you have any questions, or happen to have any 
suggestions on improving either part, the client in particular, 
as I am no PHP programmer but hacked it together from an example 
telnet client I found on the net.  I'd be particularly interested if 
you had any idea about the wisdom of using fgets to read the response 
data vs some other PHP function.

-Michel
