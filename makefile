all:
	(echo "#!"`which python` && curl -s https://war.cflems.net/warcrypto.py && cat pkd_stub.py) >pkd.py
clean:
	rm -f pkd.py *.pid *.sock *.log
