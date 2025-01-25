<!DOCTYPE html>
<html lang="en">
    <head>
<?php
require('include/meta.php');
?>
        <title>Hosts Database | Docs | Penguin&apos;s Kiss</title>
        <link rel="canonical" href="https://c2.pkctl.org/hdb" />
    </head>
<?php
require('include/header.php');
?>
                <p>Now that we&apos;ve generated our host key and gotten our server up and running, its
                    time to publish its public key in a hosts database file so that it can be retrieved
                    by clients. The TL;DR for this section is to create a file that looks like this:</p>
                <pre>{"keys": {"&lt;server ip&gt;": {"n": &lt;number n that python spit out&gt;, "e": 65537}}}</pre>
                <p>and upload it to the web somewhere. You can then supply this URL to your clients as
                    your hosts database. Literally even a PasteBin will work if you use the raw file
                    URL.</p>
                <section id="format">
                    <h3>Format</h3>
                    <p>The hosts database is essentially just a JSON object in which the PK client will
                        look for specific keys to retrieve information. The basic skeleton looks like
                        this:</p>
                    <pre>{"keys": {&lt;keys section&gt;}}</pre>
                </section>
                <section id="keys">
                    <h3>Keys Section</h3>
                    <p>The keys section is just a mapping from server IPs to key objects, which in
                        turn are just a way of representing RSA public keys. The keys section supports
                        multiple server IPs, but currently only one public key per server IP. Its
                        skeleton looks like the following:</p>
                    <pre>{"0.1.2.3": {&lt;key object&gt;}, "255.255.255.255": {&lt;key object&gt;}}</pre>
                    <h4>Key Objects</h4>
                    <p>A key object is just a modulus and a public exponent, both of which are integers.
                        The modulus is at key <code>n</code> and the public exponent is at key
                        <code>e</code>. The public exponent is optional and defaults to
                        <code>65537</code> if not supplied. These values can be pulled directly from
                        <code>/etc/pk/server_key.json</code>, but it is important to delete the
                        <code>d</code> key and its value, as this information needs to remain secret.
                    </p>
                    <p>The format of a key object is as follows:</p>
                    <pre>{"n": 3043289324798327498257285749857984257249857245, "e": 12345}</pre>
                </section>
<?php
require('include/footer.php');
?>
</html>
