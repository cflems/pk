all:
	php -f index.php >live/index.html
	php -f client.php >live/client.html
	php -f server.php >live/server.html
	php -f hdb.php >live/hdb.html
	php -f commands.php >live/commands.html
