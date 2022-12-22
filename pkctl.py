#!/usr/bin/python3
import os, sys, signal, socket, threading, time

# basic config
SOCKET_FILE = "/run/pk/pk.sock"
PID_FILE = "/run/pk/pk.pid"
DAEMON_FILE = "/usr/bin/pkd"
LOGFILE = "/var/log/pk.log"
KEY_FILE = "/etc/pk/server_key.json"
DAEMON_PORT = 2236
DAEMON_BITS = 4096

def isd_running():
    return os.path.isfile(PID_FILE)

def startd():
    os.setuid(DAEMON_UID)
    os.setgid(DAEMON_GID)
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

def attach_reader(sock, state):
    while state['attached']:
        try:
            data = sock.recv(1024)
        except:
            data = b'\xde\xad'
        if data == b'\xde\xad':
            state['attached'] = False
            break
        if len(data) > 0:
            pnnl(str(data, 'utf-8'))
    sock.close()
    threading.main_thread().join()

def attach_cmd():
    if not isd_running():
        return False

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    state = {}
    reader_thread = threading.Thread(target=attach_reader, args=(sock, state))

    try:
        sock.connect(SOCKET_FILE)
    except:
        sock.close()
        return False
    state['attached'] = True
    reader_thread.start()
    while state['attached']:
        try:
            line = input().strip()
        except EOFError:
            print('detach')
            line = 'detach'
        if line == 'detach':
            try:
                sock.sendall(b'\xde\xad')
            except:
                pass
            state['attached'] = False
        elif line == 'clear':
            os.system('clear')
            line = '\xc0\xdeprompt'
        elif len(line) < 1:
            line = '\xc0\xdeprompt'
        if not state['attached']:
            break
        try:
            sock.sendall(bytes(line, 'utf-8'))
        except:
            state['attached'] = False
            break

    sock.close()
    return True

def exec_cmd(*args):
    pass

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
            print('Cannot contact daemon; ensure it is running.')
    else:
        print('Unrecognized command:', sys.argv[1])
        print_help()
if __name__ == '__main__':
    main()
