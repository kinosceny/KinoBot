dev-build:
	docker compose -f deploy/compose.yaml -p kinobot build --no-cache

dev-start:
	docker compose -f deploy/compose.yaml -p kinobot up -d --force-recreate --remove-orphans

dev-stop:
	docker compose -f deploy/compose.yaml -p kinobot down

clone-dev-build:
	docker compose -f deploy/clone-compose.yaml -p kinobot-clone build --no-cache

clone-dev-start:
	docker compose -f deploy/clone-compose.yaml -p kinobot-clone up -d --force-recreate --remove-orphans

clone-dev-stop:
	docker compose -f deploy/clone-compose.yaml -p kinobot-clone down