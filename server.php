<!DOCTYPE html>
<html lang="en">
    <head>
<?php
require('include/meta.php');
?>
        <title>Server Configuration | Docs | Penguin&apos;s Kiss</title>
        <link rel="canonical" href="https://c2.pkctl.org/server" />
    </head>
<?php
require('include/header.php');
?>
                <p>Once your PK scripts are built very little is required to run the server as a local
                    user, you can literally just do:</p>
                <pre>python3 pkctl.py start
python3 pkctl.py attach</pre>
                <p>and have yourself a simple instance up and running ready to run commands. Therefore
                    the rest of this section will be dedicated to getting PK running in the background
                    as a systemd service under its own user, and letting multiple system users attach
                    to the daemon at once if desired.</p>
                <section id="install">
                    <h3>Installing</h3>
                    <p>Once again the makefile mostly has you covered here, all you need to do is:</p>
                    <pre>sudo make install</pre>
                    <p>and the makefile will set up a dedicated service user and group called
                        <code>pkd</code> which controls access to the daemon and its resources, as well
                        as setting up the pk server as a systemd service called <code>pk</code>. This
                        will also start the pk server and enable it on startup.</p>
                </section>
                <section id="pkctl">
                    <h3>PKCTL Usage</h3>
                    <p>Once installed, you can use the following commands to interface with the pk
                        daemon controller:</p>
                    <p><code>systemctl start|stop|restart pk</code> &mdash; this controls the
                        daemon&apos;s life cycle.</p>
                    <p><code>pkctl attach</code> &mdash; this starts an interactive session with the
                        daemon, allowing you to control and interface with clients.</p>
                </section>
                <section id="keygen">
                    <h3>Host Key Generation</h3>
                    <p>Once you&apos;ve installed the pk server you&apos;re going to want to change its
                        host key away from the default one which is used for testing purposes and is
                        widely available (read: not secure at all).</p>
                    <p>This is probably the only complicated part of the whole guide, mostly because
                        I haven&apos;t yet built a cute little utility to do it for you yet (I should
                        at some point). You&apos;re going to need to do the following (in your pk
                        directory):</p>
                    <pre>python3
&gt;&gt;&gt; import crypto
&gt;&gt;&gt; p,q,n,e,d = crypto.Crypto.keygen(4096)
&gt;&gt;&gt; n</pre>
                    <p>Copy the number that python spits out here.</p>
                    <pre>
&gt;&gt;&gt; d</pre>
                    <p>Also copy this number. Keep these two handy as we&apos;ll need them later.
                        Now open <code>/etc/pk/server_key.json</code> in your favorite editor and make
                        it read as follows (you can wipe out the current contents):</p>
                    <pre>{"n": &lt;the number n we got from python&gt;, "d": &lt;the number d we got from python&gt;, "e": 65537}</pre>
                    <p>At this point we&apos;re almost done, we just have to restart pk to reflect the
                        changes, so run:</p>
                    <pre>sudo systemctl restart pk</pre>
                    <p>and you should be good to go.</p>
                </section>
                <section id="users">
                    <h3>Local Users</h3>
                    <p>To allow non-root users on your system to use <code>pkctl attach</code>, you
                        will need to add them to the <code>pkd</code> user group. This is remarkably
                        simple to do on any unix system, just run:</p>
                    <pre>adduser [username] pkd</pre>
                </section>
<?php
require('include/footer.php');
?>
</html>
