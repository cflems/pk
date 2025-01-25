<!DOCTYPE html>
<html lang="en">
    <head>
<?php
require('include/meta.php');
?>
        <title>Command Reference | Docs | Penguin&apos;s Kiss</title>
        <link rel="canonical" href="https://c2.pkctl.org/commands" />
    </head>
<?php
require('include/header.php');
?>
                <p>The following commands can be executed while attached to the daemon via
                    <code>pkctl attach</code>.</p>
                <section id="beacon">
                    <h3>beacon</h3>
                    <p>Creates a DNS beacon that this host will respond to as if it were a legitimate
                        DNS server. If a beacon already exists at this hostname, record type, and
                        record class, it will be overwritten.</p>
                    <p>Arguments: DNS data (hex string), hostname (string), record type (string),
                        record class (string, optional).</p>
                    <p>DNS data must be a string representing the hex-encoded binary data to be
                        returned as the answer to a DNS query for this record.</p>
                    <p>Hostname is the DNS hostname for which to answer queries.</p>
                    <p>Record type must be one of A, AAAA, CNAME, MX, or TXT. Data must be formatted
                        correctly per record type or else malformed responses will be returned.</p>
                    <p>Record class must be one of IN, CH, or HS, or else omitted. Defaults to IN
                        (the internet).</p>
                    <p>Usage:</p>
                    <pre>pk&gt; beacon 01020304 x.z.pkctl.org A IN</pre>
                </section>
                <section id="delbeacon">
                    <h3>delbeacon</h3>
                    <p>Deletes one or more beacons according to arguments supplied. If only hostname
                        is supplied, all beacons matching hostname will be deleted. If more arguments
                        are supplied, the search will be narrowed accordingly.</p>
                    <p>Arguments: hostname (string), record type (string, optional), record class
                        (string, optional).</p>
                    <p>See <a href="#beacon">beacon reference</a> for the meanings of these arguments.</p>
                    <p>Usage:</p>
                    <pre>pk&gt; delbeacon x.z.pkctl.org A IN</pre>
                </section>
                <section id="nbeacons">
                    <h3>nbeacons</h3>
                    <p>Prints the number of currently active DNS beacons.</p>
                    <p>Usage:</p>
                    <pre>pk&gt; nbeacons
[pk] Active beacons: 224</pre>
                </section>
                <section id="lbeacons">
                    <h3>lbeacons</h3>
                    <p>Lists all currently active DNS beacons and their data.</p>
                    <p>Usage:</p>
                    <pre>pk&gt; lbeacons
[pk] Active beacons:
- x.z.pkctl.org A IN: 01020304
- ...
[pk] 224 total.</pre>
                </section>
                <section id="nscreen">
                    <h3>nscreen</h3>
                    <p>Prints the number of currently attached controller screens.</p>
                    <p>Usage:</p>
                    <pre>pk&gt; nscreen
[pk] Active screens: 2</pre>
                </section>
                <section id="ncli">
                    <h3>ncli</h3>
                    <p>Prints the number of currently connected TCP clients.</p>
                    <p>Usage:</p>
                    <pre>$ ncli
[pk] Active TCP clients: 27</pre>
                </section>
                <section id="lcli">
                    <h3>lcli</h3>
                    <p>Lists the currently connected TCP clients and their descriptive information.</p>
                    <pre>$ lcli
[pk] Active TCP clients:
- 0: {'ip': '127.0.0.1', 'rport': 47874, 'rdns': 'localhost'}
- ...
[pk] 27 total.</pre>
                </section>
                <section id="lq">
                    <h3>lq</h3>
                    <p>Lists the queue of commands to be executed by newly connected clients.</p>
                    <p>Usage:</p>
                    <pre>pk&gt; lq
['whoami', 'hostname']</pre>
                </section>
                <section id="cq">
                    <h3>cq</h3>
                    <p>Clears the command queue.</p>
                    <p>Usage:</p>
                    <pre>pk&gt; cq</pre>
                </section>
                <section id="show-serverkey">
                    <h3>show-serverkey</h3>
                    <p>Prints the server&apos;s public key in a format easily copyable into an HDB
                        entry.</p>
                    <p>Usage:</p>
                    <pre>pk&gt; show-serverkey
{"n": ..., "e": ...}</pre>
                </section>
                <section id="pty">
                    <h3>pty</h3>
                    <p>Connects your screen to the specified client in a one-on-one terminal session,
                        similar to SSHing into the client machine.</p>
                    <p>Arguments: client ID (integer) &mdash; can be found with <code>lcli</code>.</p>
                    <p>Usage:</p>
                    <pre>$ pty 3</pre>
                </section>
                <section id="refresh-hdb">
                    <h3>refresh-hdb</h3>
                    <p>Commands the client to refresh its internal hosts database from the web resource
                        it was originally pulled from.</p>
                    <p>Usage:</p>
                    <pre>$ refresh-hdb</pre>
                </section>
                <section id="tunnel">
                    <h3>tunnel</h3>
                    <p>Commands the client to disconnect and sleep for the number of seconds configured
                        in <a href="/client#tts">TTS</a>.</p>
                    <p>Usage:</p>
                    <pre>$ tunnel</pre>
                </section>
                <section id="die">
                    <h3>die</h3>
                    <p>Commands the client to exit and not respawn.</p>
                    <p>Usage:</p>
                    <pre>$ die</pre>
                </section>
                <section id="shell">
                    <h3>Shell Commands</h3>
                    <p>Inputs which are not recognized as server commands will be interpreted as
                        shell commands, which will be blasted to all connected clients and queued for
                        future clients to receive as well. Once executed, the results of these
                        commands will be blasted to all active screens, and logged in case no screen
                        is watching at the time of the response. The active command queue can be
                        managed by way of the <a href="#lq">lq</a> and <a href="#cq">cq</a>
                        commands.</p>
                </section>
                <section id="target">
                    <h3>Targeting</h3>
                    <p>In the event that you would prefer not to dispatch a command to all current and
                        future clients, a specific set of targets can be specified by prepending
                        <code>TARGET={targets}</code> to the command, where <code>{targets}</code> is
                        a comma-delimited list of client IDs (integers). These client IDs can be
                        retrieved by checking the output of <code>lcli</code>. Commands which are
                        targeted are not queued for future clients to receive.</p>
                    <p>Usage:</p>
                    <pre>$ TARGET=0,4,57,264 echo hello</pre>
                </section>
<?php
require('include/footer.php');
?>
</html>
