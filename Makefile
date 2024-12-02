install:
	poetry install

runserver:
	fastapi dev mdp2mailservice/main.py --host 0.0.0.0 --port 8000

test:
	export ENVIRONMENT=test && pytest .

migration:
	alembic revision --autogenerate -m "$(message)"

migrate:
	alembic upgrade head

docker_build:
	docker-compose up -d --build