import random, secrets, math

class Crypto:
    exp = 0x10001
    rand_pad = 4
    low_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699, 1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789, 1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889, 1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997, 1999, 2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113, 2129, 2131, 2137, 2141, 2143, 2153, 2161, 2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269, 2273, 2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351, 2357, 2371, 2377, 2381, 2383, 2389, 2393, 2399, 2411, 2417, 2423, 2437, 2441, 2447, 2459, 2467, 2473, 2477, 2503, 2521, 2531, 2539, 2543, 2549, 2551, 2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659, 2663, 2671, 2677, 2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719, 2729, 2731, 2741, 2749, 2753, 2767, 2777, 2789, 2791, 2797, 2801, 2803, 2819, 2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909, 2917, 2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999, 3001, 3011, 3019, 3023, 3037, 3041, 3049, 3061, 3067, 3079, 3083, 3089, 3109, 3119, 3121, 3137, 3163, 3167, 3169, 3181, 3187, 3191, 3203, 3209, 3217, 3221, 3229, 3251, 3253, 3257, 3259, 3271, 3299, 3301, 3307, 3313, 3319, 3323, 3329, 3331, 3343, 3347, 3359, 3361, 3371, 3373, 3389, 3391, 3407, 3413, 3433, 3449, 3457, 3461, 3463, 3467, 3469, 3491, 3499, 3511, 3517, 3527, 3529, 3533, 3539, 3541, 3547, 3557, 3559, 3571]

    def byte_length (i):
        return -(-i.bit_length()//8)
    def i2b (i, sz=None):
        return i.to_bytes(sz if sz else Crypto.byte_length(i), 'big')
    def b2i (b):
        return int.from_bytes(b, 'big')

    def pcand(bits):
        return (1 << (bits-1)) | random.getrandbits(bits-1) | 1

    def psafe1(cand):
        for n in Crypto.low_primes:
            if n**2 > cand:
                return True
            elif cand % n == 0:
                return False
        return True

    def pgen1(bits):
        while True:
            cand = Crypto.pcand(bits)
            if Crypto.psafe1(cand):
                return cand

    def psafe2(cand, rounds=20):
        s = 0
        d = cand-1
        while d & 1 == 0:
            d >>= 1
            s += 1
        for i in range(rounds):
            a = random.randrange(2, cand)
            if pow(a, d, cand) == 1:
                return True
            for r in range(s):
                if pow(a, 2**r * d, cand) == cand-1:
                    return True
        return False

    def pgen(bits):
        while True:
            cand = Crypto.pgen1(bits)
            if Crypto.psafe2(cand):
                return cand

    def headsize(bits):
        return Crypto.byte_length(-(-bits//8))

    def pad(m, bits):
        headsz = Crypto.headsize(bits)
        chunks, nbytes = [], -(-bits//8)-headsz-Crypto.rand_pad-1

        while len(m) > nbytes:
            chunk = Crypto.i2b(nbytes, headsz) + m[:nbytes] + secrets.token_bytes(Crypto.rand_pad)
            m = m[nbytes:]
            chunks.append(Crypto.b2i(chunk))
        chunk = Crypto.i2b(len(m), headsz) + m + secrets.token_bytes(nbytes - len(m) + Crypto.rand_pad)
        chunks.append(Crypto.b2i(chunk))
        return chunks

    def unpad(p, bits):
        nbytes = -(-bits//8) - 1
        m_chunks, headsz = [], Crypto.headsize(bits)
        for p_chunk in p:
            chunk = Crypto.i2b(p_chunk, nbytes)
            chunksz = Crypto.b2i(chunk[:headsz])
            m_chunks.append(chunk[headsz:headsz+chunksz])
        return b''.join(m_chunks)

    def encrypt(m, e, n, bits):
        nbytes = -(-bits//8)
        return [Crypto.i2b(pow(p, e, n), nbytes) for p in Crypto.pad(m, bits)]

    def decrypt(p, d, n, bits):
        return Crypto.unpad([pow(Crypto.b2i(c), d, n) for c in p], bits)

    def keygen(bits=2048):
        p, q = Crypto.pgen(bits >> 1), Crypto.pgen(bits >> 1)
        #p = 24255437060933278568327701135893465111281929996020213283563016322587538898307222832676648856557095025772204413206980826822975131457046546497523091381599846376591186469347076218208800469787851326371447052505831886762813382071182380079565671280034572474822918684998169291052805586193101619898239325398349038870346792747848088462443207267957917761324031277878527517794286421236832567949642803568424614512153948596887559236723641422745633542467824845355764889656771928727895545492980157734692593529905622895318376798465152794082339714326113478586369772394086511968434509576965140800722212375216417198365996986997884522143
        #q = 19768976408982925938974295924028441291658237346176654371253117928175549332214544184956873153703986985390178340362842925095394171723247001148381841608957916206559941167745803865591902614480793421765383057879093169950619962622549993022767924551441062799960937735273562540998394372954466434657886766982923637838307867760458002688852634523140205959841808840422174672818444274740218202285908370264201317843186892579386846520240651724201292430263438230872027782342582077071631797326347450149692183612550505452085046398227369191676244454566325746209776357595496074364519226187538979254031364601406997434831185228055585873117
        n, e, d = p*q, Crypto.exp, pow(Crypto.exp, -1, (p-1)*(q-1))
        return p, q, n, e, d

class PKSock:
    def __init__ (self, sock, priv, bits):
        self.sock = sock
        self.priv = priv
        if 'e' not in priv:
            self.priv['e'] = Crypto.exp
        self.bits = bits
        self.nbytes = -(-bits//8)
        self.headsz = Crypto.byte_length(self.nbytes)
        self.streaming = False
        self.isk = None
        self.iskp = 0
        self.osk = None
        self.oskp = 0
        self.sksz = self.nbytes - self.headsz - Crypto.rand_pad - 1
        self.read_buffer = False
        self.buffer = b''

    def start_stream (self):
        self.isk = None
        self.osk = None
        self.iskp = 0
        self.oskp = 0
        self.streaming = True
        self.read_buffer = False
        self.buffer = b''

    def stop_stream (self, backtrack=0):
        assert (backtrack <= self.nbytes)
        self.isk = None
        self.osk = None
        self.iskp = 0
        self.oskp = 0
        self.buffer = self.buffer[-backtrack:]
        self.read_buffer = backtrack > 0
        self.streaming = False

    def raw_send (self, b):
        self.sock.sendall(b)

    def raw_recv (self, n):
        msg = b''
        if self.read_buffer and len(self.buffer) > 0:
            msg += self.buffer[:n]
            self.buffer = self.buffer[n:]
        if len(msg) < n:
            msg += self.sock.recv(n-len(msg))
        return msg
    
    def raw_cache (self, b):
        assert(type(b) == bytes)
        self.read_buffer = False
        if len(b) < self.nbytes:
            off = self.nbytes - len(b)
            self.buffer = self.buffer[len(b) - self.nbytes:] + b
        else:
            self.buffer = b[-self.nbytes:]
    
    def send (self, b, force_normal=False):
        assert(type(b) == bytes)
        if len(b) < 1:
            return
        
        if self.streaming and not force_normal:
            if not self.osk or self.oskp >= len(self.osk):
                self.push_sk()
            while len(b) > len(self.osk) - self.oskp:
                b_frag = b[:len(self.osk)-self.oskp]
                k = self.osk[self.oskp:]
                c = bytes([b_frag[i] ^ k[i] for i in range(len(b_frag))])
                self.sock.sendall(c)
                b = b[len(b_frag):]
                self.push_sk()
            if len(b) > 0:
                k = self.osk[self.oskp:self.oskp+len(b)]
                c = bytes([b[i] ^ k[i] for i in range(len(b))])
                self.sock.sendall(c)
                self.oskp += len(b)
        else:
            p = Crypto.encrypt(b, self.rpk['e'], self.rpk['n'], self.bits)
            self.raw_send(Crypto.i2b(len(p), self.headsz))
            for chunk in p:
                self.raw_send(chunk)

    def recv (self, force_normal=False):
        if self.streaming and not force_normal:
            if not self.isk or self.iskp >= len(self.isk):
                self.pull_sk()
            # TODO: this could use some work because we can split opcodes etc
            c = self.raw_recv(len(self.isk) - self.iskp)
            self.raw_cache(c)
            k = self.isk[self.iskp : self.iskp+len(c)]
            self.iskp += len(c)
            return bytes([c[i] ^ k[i] for i in range(len(c))])
        else:
            chunks, nchunks = [], Crypto.b2i(self.raw_recv(self.headsz))
            for _ in range(nchunks):
                chunks.append(self.raw_recv(self.nbytes))
            return Crypto.decrypt(chunks, self.priv['d'], self.priv['n'], self.bits)

    def handshake_client (self):
        rnbytes = Crypto.b2i(self.raw_recv(self.headsz))
        self.raw_send(Crypto.i2b(self.nbytes, self.headsz))
        if self.nbytes != rnbytes:
            return False
        
        self.rpk = {'n': Crypto.b2i(self.recv()), 'e': Crypto.exp}
        return True

    def handshake_server (self, server_pk):
        self.rpk = server_pk
        self.raw_send(Crypto.i2b(self.nbytes, self.headsz))
        rnbytes = Crypto.b2i(self.raw_recv(self.headsz))
        if self.nbytes != rnbytes:
            return False
        self.send(Crypto.i2b(self.priv['n'], self.nbytes))
        return True

    def push_sk (self):
        self.osk = secrets.token_bytes(self.sksz)
        self.oskp = 0
        self.send(self.osk, force_normal=True)

    def pull_sk (self):
        self.isk = self.recv(force_normal=True)
        self.iskp = 0

    def close (self):
        self.sock.close()
