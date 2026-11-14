.PHONY: up seed eval lint
up:
	docker compose up --build
seed:
	docker compose exec api python -m app.seed
eval:
	python evals/run_evals.py
lint:
	ruff check backend evals
