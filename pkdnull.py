import os, socket, sys, signal

if len(sys.argv) < 4:
    print('Bad arguments; exit.')
    sys.exit(1)
elif len(sys.argv) > 4:
    print('Extra args:', sys.argv[4:])

SOCKET_FILE = sys.argv[1]
PID_FILE = sys.argv[2]
LOG_FILE = sys.argv[3]

if os.path.exists(PID_FILE):
    print('Already running; exit.')
    sys.exit(1)

if os.fork() != 0:
    sys.exit(0)

def cleanup():
    global cs, sock
    try:
        cs.close()
    except:
        pass
    sock.close()
    os.remove(PID_FILE)
    os.remove(SOCKET_FILE)
    os.close(sys.stdout.fileno())
    os.close(sys.stderr.fileno())


def stopsig(*args):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, stopsig)
logfd = os.open(LOG_FILE, os.O_WRONLY | os.O_APPEND | os.O_CREAT, mode=0o644)
os.close(sys.stdin.fileno())
os.dup2(logfd, sys.stdout.fileno())
os.dup2(logfd, sys.stderr.fileno())
os.close(logfd)

pidf = open(PID_FILE, 'w')
pidf.write('%d' % os.getpid())
pidf.close()

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind(SOCKET_FILE)
sock.listen(5)

try:
    cs, ca = sock.accept()
    while True:
        cs.send(b'$ ')
        data = cs.recv(1024)
        if data == b'\xde\xad':
            break
        print('got some data: %s' % str(data, 'utf-8'))
        cs.send(data+b'\n')
finally:
    cleanup()
