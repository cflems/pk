#!/usr/bin/python3
import os, sys, signal, socket, selectors, time, tty

# basic config
#SOCKET_FILE = "/run/pk/pk.sock"
#PID_FILE = "/run/pk/pk.pid"
#DAEMON_FILE = "/usr/bin/pkd"
#LOG_FILE = "/var/log/pk.log"
#KEY_FILE = "/etc/pk/server_key.json"

SOCKET_FILE = "./pk.sock"
PID_FILE = "./pk.pid"
DAEMON_FILE = "python pkd.py"
LOG_FILE = "./pk.log"
KEY_FILE = "./default_key.json"
DAEMON_PORT = 2236
DAEMON_BITS = 4096

def isd_running():
    return os.path.isfile(PID_FILE)

def startd():
    return os.system('%s %s %s %s %d %d %s' % (DAEMON_FILE, SOCKET_FILE,\
                                               PID_FILE, LOG_FILE, \
                                               DAEMON_BITS, DAEMON_PORT,\
                                               KEY_FILE))

def signald(sig):
    if not isd_running():
        return False
    pidf = open(PID_FILE, 'r')
    pid = int(pidf.read().strip())
    pidf.close()
    try:
        os.kill(pid, sig)
    except ProcessLookupError:
        os.remove(PID_FILE)
        return False
    return True

def pnnl(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def print_help():
    print('Usage: %s COMMAND [OPTIONS]...' % sys.argv[0])
    print('Dispatch COMMAND to the PK Daemon.')
    print('Example: %s attach' % sys.argv[0])
    print()
    print('Commands:')
    print('\tstart\t\t\t\tstart the daemon')
    print('\tstop\t\t\t\tstop the daemon')
    print('\trestart\t\t\t\trestart the daemon')
    print('\tattach\t\t\t\tcontrol the daemon via attached screen')

def start_cmd():
    return startd() == 0

def stop_cmd():
    return signald(signal.SIGTERM)

def attach_cmd():
    if not isd_running():
        return False

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(SOCKET_FILE)
    except:
        sock.close()
        return False
    sel = selectors.DefaultSelector()
    sel.register(sys.stdin.fileno(), selectors.EVENT_READ, 0)
    sel.register(sock, selectors.EVENT_READ, 1)
    attached = True
    pty_mode = False
    stdin_mode = None

    while attached:
        events = sel.select()
        for event, mask in events:
            if event.data == 0:
                try:
                    data = os.read(sys.stdin.fileno(), 1024)
                except Exception:
                    data = False
                if not data:
                    attached = False
                    break
                elif pty_mode:
                    try:
                        sock.sendall(data)
                        continue
                    except:
                        attached = False
                        break
                elif data.strip() == b'detach':
                    try:
                        sock.sendall(b'\xde\xad')
                    except:
                        pass
                    attached = False
                    break
                elif data.strip() == b'clear':
                    os.system('clear')
                    data = b'\xc0\xdeprompt'
                elif len(data.strip()) < 1:
                    data = b'\xc0\xdeprompt'
                try:
                    sock.sendall(data)
                except:
                    attached = False
                    break
            else:
                try:
                    data = sock.recv(1024)
                except Exception:
                    data = False
                if not data or data == b'\xde\xad':
                    if pty_mode:
                        tty.tcsetattr(sys.stdin.fileno(), tty.TCSAFLUSH, stdin_mode)
                        pty_mode = False
                        print('turned off pty mode due to remote detach')
                    attached = False
                    break
                elif pty_mode and data[:6] == b'\xc0\xdenpty':
                    tty.tcsetattr(sys.stdin.fileno(), tty.TCSAFLUSH, stdin_mode)
                    pty_mode = False
                    print('turned off pty mode due to npty command')
                    if len(data) > 6:
                        pnnl(str(data[6:], 'utf-8'))
                elif not pty_mode and data == b'\xc0\xdepty':
                    pty_mode = True
                    stdin_mode = tty.tcgetattr(sys.stdin.fileno())
                    tty.setraw(sys.stdin.fileno())
                else:
                    pnnl(str(data, 'utf-8'))
    sel.close()
    sock.close()
    if pty_mode:
        tty.tcsetattr(sys.stdin.fileno(), tty.TCSAFLUSH, stdin_mode)
    return True

def main():
    if len(sys.argv) < 2 or sys.argv[1] == 'help':
        print_help()
    elif sys.argv[1] == 'start':
        if len(sys.argv) > 2:
            print('Unrecognized option(s):', *sys.argv[2:])
            print_help()
            return
        if start_cmd():
            print('Daemon started.')
        else:
            print('Failed to start daemon.')
    elif sys.argv[1] == 'stop':
        if len(sys.argv) > 2:
            print('Unrecognized option(s):', *sys.argv[2:])
            print_help()
            return
        if stop_cmd():
            print('Dispatched stop command to daemon.')
        else:
            print('Failed to stop daemon; ensure it is running.')
    elif sys.argv[1] == 'restart':
        if len(sys.argv) > 2:
            print('Unrecognized option(s):', *sys.argv[2:])
            print_help()
            return
        if stop_cmd():
            print('Dispatched stop command to daemon.')
            time.sleep(2)
        else:
            print('Daemon was not running so will not be stopped.')
        if start_cmd():
            print('Daemon started.')
        else:
            print('Failed to start daemon.')
    elif sys.argv[1] == 'attach':
        if len(sys.argv) > 2:
            print('Unrecognized option(s):', *sys.argv[2:])
            print_help()
            return
        if attach_cmd():
            print('Detached from daemon; quitting.')
        else:
            print('Cannot contact daemon; ensure it is running and you have access to it.')
    else:
        print('Unrecognized command:', sys.argv[1])
        print_help()
if __name__ == '__main__':
    main()
