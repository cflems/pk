all:
	(echo "#!"`which python3` && cat crypto.py && cat pkd_stub.py) >pkd.py
	(echo "#!"`which python3` && cat crypto.py && cat pkcli_stub.py) >pkcli.py
clean:
	rm -f pkd.py pkcli.py *.pid *.sock *.log
test:
	python3 pkcli.py localhost 30 4096
	python3 pkd.py pk.sock pk.pid pk.log 4096 2236 default_key.json
install:
	useradd -rUs /usr/sbin/nologin pkd || true
	mkdir -p /run/pk /etc/pk
	chmod 0755 /run/pk
	chmod 0700 /etc/pk
	touch /var/log/pk.log
	chown pkd:pkd /var/log/pk.log
	chmod 0640 /var/log/pk.log
	cp ./default_key.json /etc/pk/server_key.json
	chmod 0600 /etc/pk/server_key.json
	chown -R pkd:pkd /etc/pk /run/pk
	cp ./pkd.py /usr/bin/pkd
	cp ./pkctl.py /usr/bin/pkctl
	chmod 0755 /usr/bin/pkd /usr/bin/pkctl
	chown root:root /usr/bin/pkd /usr/bin/pkctl
	cp ./pk.service /lib/systemd/system/pk.service
	chown root:root /lib/systemd/system/pk.service
	chmod 0644 /lib/systemd/system/pk.service
	systemctl daemon-reload
	systemctl enable pk.service
	systemctl start pk.service
