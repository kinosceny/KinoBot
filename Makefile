dev-build:
	docker compose -f deploy/compose.yaml -p kinobot build --no-cache

dev-start:
	docker compose -f deploy/compose.yaml -p kinobot up -d --force-recreate --remove-orphans
