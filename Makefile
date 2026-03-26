.PHONY: install load-data api dashboard docker-up docker-down clean

install:
	pip install -r requirements.txt

load-data:
	python -m src.knowledge.sample_guidelines
	python -m src.knowledge.medical_data_loader

api:
	uvicorn src.api.app:app --reload --port 8000

dashboard:
	streamlit run src/dashboard/app.py --server.port 8501

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

clean:
	rm -rf data/chromadb __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
