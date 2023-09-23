import mpd
import socket

class PersistentMPDClient(mpd.MPDClient):
    def __init__(self, socket=None, host=None, port=None):
        super(PersistentMPDClient, self).__init__()
        self.socket = socket
        self.host   = host
        self.port   = port

        self.do_connect()
        # get list of available commands from client
        self.command_list = self.commands()

        # commands not to intercept
        self.command_blacklist = ['ping']

        # wrap all valid MPDClient functions
        # in a ping-connection-retry wrapper
        for cmd in self.command_list:
            if cmd not in self.command_blacklist:
                if hasattr(super(PersistentMPDClient, self), cmd):
                    super_fun = super(PersistentMPDClient, self).__getattribute__(cmd)
                    new_fun = self.try_cmd(super_fun)
                    print("Setting interceptor for {}".format(cmd))
                    setattr(self, cmd, new_fun)
                else:
                    print("Attr {} not available!".format(cmd))

    # create a wrapper for a function (such as an MPDClient
    # member function) that will verify a connection (and
    # reconnect if necessary) before executing that function.
    # functions wrapped in this way should always succeed
    # (if the server is up)
    # we ping first because we don't want to retry the same
    # function if there's a failure, we want to use the noop
    # to check connectivity
    def try_cmd(self, cmd_fun):
        def fun(*pargs, **kwargs):
            try:
#                print("Attemping to ping...")
                self.ping()
            except (mpd.ConnectionError, OSError) as e:
#                print("lost connection.")
#                print("trying to reconnect.")
                self.do_connect()
            return cmd_fun(*pargs, **kwargs)
        return fun

    # needs a name that does not collide with parent connect() function
    def do_connect(self):
        try:
            try:
#                print("Attempting to disconnect.")
                self.disconnect()
            # if it's a TCP connection, we'll get a socket error
            # if we try to disconnect when the connection is lost
            except mpd.ConnectionError as e:
#                print("Disconnect failed, so what?")
                pass
            # if it's a socket connection, we'll get a BrokenPipeError
            # if we try to disconnect when the connection is lost
            # but we have to retry the disconnect, because we'll get
            # an "Already connected" error if we don't.
            # the second one should succeed.
            except BrokenPipeError as e:
#                print("Pipe closed, retrying disconnect.")
                try:
#                    print("Retrying disconnect.")
                    self.disconnect()
                except Exception as e:
                    print("Second disconnect failed, yikes.")
                    print(e)
                    pass
            if self.socket:
#                print("Connecting to {}".format(self.socket))
                self.connect(self.socket, None)
            else:
#                print("Connecting to {}:{}".format(self.host, self.port))
                self.connect(self.host, self.port)
        except socket.error as e:
            print("Connection refused.")
#            print(e)

