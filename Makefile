lint:
	poetry run ruff check bulk_copy tests --fix
	poetry run mypy bulk_copy


test:
	docker-compose up -d

	until [ "`docker inspect -f {{.State.Health.Status}} CONTAINERNAME`"=="healthy" ]; do sleep 0.1; done;

	poetry run python manage.py migrate
	poetry run pytest

	docker-compose down -v

tox: # TODO: fix tox run
	docker-compose up -d

	until [ "`docker inspect -f {{.State.Health.Status}} CONTAINERNAME`"=="healthy" ]; do sleep 0.1; done;

	poetry run python manage.py migrate
	poetry run tox

	docker-compose down -v
