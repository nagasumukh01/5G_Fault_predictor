.PHONY: install train run-backend run-frontend run test docker-up docker-down

install:
	pip install -r requirements.txt
	cd frontend && npm install

train:
	python scripts/train_and_eval.py

run-backend:
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

run:
	@echo "Starting full local stack..."
	@echo "Open Terminal 1: make run-backend"
	@echo "Open Terminal 2: make run-frontend"

test:
	pytest tests -v

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
