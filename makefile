all:
	php -f index.php >docs/index.html
	php -f client.php >docs/client.html
	php -f server.php >docs/server.html
	php -f hdb.php >docs/hdb.html
	php -f commands.php >docs/commands.html
