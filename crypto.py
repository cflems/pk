import random, secrets, math

class Crypto:
    exp = 0x10001
    rand_pad = 4
    low_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609, 1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699, 1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789, 1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889, 1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997, 1999, 2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113, 2129, 2131, 2137, 2141, 2143, 2153, 2161, 2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269, 2273, 2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351, 2357, 2371, 2377, 2381, 2383, 2389, 2393, 2399, 2411, 2417, 2423, 2437, 2441, 2447, 2459, 2467, 2473, 2477, 2503, 2521, 2531, 2539, 2543, 2549, 2551, 2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659, 2663, 2671, 2677, 2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719, 2729, 2731, 2741, 2749, 2753, 2767, 2777, 2789, 2791, 2797, 2801, 2803, 2819, 2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909, 2917, 2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999, 3001, 3011, 3019, 3023, 3037, 3041, 3049, 3061, 3067, 3079, 3083, 3089, 3109, 3119, 3121, 3137, 3163, 3167, 3169, 3181, 3187, 3191, 3203, 3209, 3217, 3221, 3229, 3251, 3253, 3257, 3259, 3271, 3299, 3301, 3307, 3313, 3319, 3323, 3329, 3331, 3343, 3347, 3359, 3361, 3371, 3373, 3389, 3391, 3407, 3413, 3433, 3449, 3457, 3461, 3463, 3467, 3469, 3491, 3499, 3511, 3517, 3527, 3529, 3533, 3539, 3541, 3547, 3557, 3559, 3571]

    def byte_length (i):
        return -(-i.bit_length()//8)
    def i2b (i):
        return i.to_bytes(Crypto.byte_length(i), 'big')
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
        chunks, nbytes = [], bits//8-headsz-Crypto.rand_pad-1

        while len(m) > nbytes:
            chunk = Crypto.i2b(nbytes) + m[:nbytes]
            m = m[nbytes:]
            chunks.append(Crypto.b2i(chunk))
        chunk = Crypto.i2b(len(m)) + m + secrets.token_bytes(nbytes - len(m) + Crypto.rand_pad)
        chunks.append(int.from_bytes(chunk, 'big'))
        return chunks

    def unpad(p, bits):
        m_chunks, headsz = [], bits//8-1, Crypto.headsize(bits)
        for p_chunk in p:
            chunk = Crypto.i2b(p_chunk)
            chunksz = Crypto.b2i(chunk[:headsz])
            m_chunks.append(chunk[headsz:headsz+chunksz])
        return b''.join(m_chunks)

    def encrypt(m, e, n, bits):
        return [Crypto.i2b(pow(p, e, n)) for p in Crypto.pad(m, bits)]

    def decrypt(p, d, n, bits):
        return Crypto.unpad([pow(Crypto.b2i(c), d, n) for c in p], bits)

    def keygen(bits=2048):
        p, q = Crypto.pgen(bits >> 1), Crypto.pgen(bits >> 1)
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
        self.sk = None
        self.skp = 0
        self.sksz = self.nbytes - self.headsz - 1
        self.buffer = b''

    def start_stream (self):
        self.sk = None
        self.skp = 0
        self.streaming = True

    def stop_stream (self, backtrack=0):
        assert (backtrack <= self.nbytes)
        self.sk = None
        self.skp = 0
        self.buffer = self.buffer[-backtrack:]
        self.streaming = False

    def raw_send (self, b):
        self.sock.sendall(b)

    def raw_recv (self, n):
        msg = b''
        if (len(self.buffer) > 0):
            msg += self.buffer[:n]
            self.buffer = self.buffer[n:]
        if (len(msg) < n):
            msg += self.sock.recv(n-len(msg))
        return msg
    
    def raw_cache (self, b):
        assert(type(b) == bytes)
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
            if not self.sk or self.skp >= len(self.sk):
                self.push_sk()
            while len(b) > len(self.sk) - self.skp:
                b_frag = b[:len(self.sk)-self.skp]
                k = self.sk[self.skp:self.skp+len(b_frag)]
                self.skp += len(b_frag)
                self.sock.sendall(bytes([b_frag[i] ^ k[i] for i in range(len(b_frag))]))
                b = b[len(b_frag):]
                self.push_sk()
            k = self.sk[self.skp:self.skp+len(b)]
            self.skp += len(b)
            self.sock.sendall(bytes([b[i] ^ k[i] for i in range(len(b))]))
        else:
            p = Crypto.encrypt(b, self.rpk['e'], self.rpk['n'], self.bits)
            self.raw_send(Crypto.i2b(len(p)))
            for chunk in p:
                self.raw_send(chunk)

    def recv (self, force_normal=False):
        if self.streaming and not force_normal:
            if not self.sk or self.skp >= len(self.sk):
                self.pull_sk()
            # TODO: this could use some work because we can split opcodes etc
            c = self.sock.recv(len(self.sk) - self.skp)
            self.raw_cache(c)
            k = self.sk[self.skp : self.skp+len(c)]
            self.skp += len(c)
            return bytes([c[i] ^ k[i] for i in range(len(c))])
        else:
            chunks, nchunks = [], Crypto.b2i(self.raw_recv(self.headsz))
            for _ in range(nchunks):
                chunks.append(self.raw_recv(self.nbytes))
            return Crypto.decrypt(chunks, self.priv['d'], self.priv['n'], self.bits)

    def handshake_client (self):
        rnbytes = Crypto.b2i(self.raw_recv(self.headsz))
        self.raw_send(Crypto.i2b(self.nbytes))
        if self.nbytes != rnbytes:
            return False
        
        self.rpk = {'n': Crypto.b2i(self.recv()), 'e': Crypto.exp}
        return True

    def handshake_server (self, server_pk):
        self.rpk = server_pk
        self.raw_send(Crypto.i2b(self.nbytes))
        rnbytes = Crypto.b2i(self.raw_recv(self.headsz))
        if self.nbytes != rnbytes:
            return False
        self.send(Crypto.i2b(self.priv['n']))

    def push_sk (self):
        self.sk = secrets.token_bytes(self.sksz)
        self.skp = 0
        self.send(self.sk, force_normal=True)

    def pull_sk (self):
        self.sk = self.recv(force_normal=True)
        self.skp = 0