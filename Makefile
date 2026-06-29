.PHONY: backend frontend train test zip

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0

train:
	cd backend && python scripts/train_xgboost.py --synthetic --output-dir models

test:
	cd backend && python -m pytest tests

zip:
	cd .. && zip -r explainable_ar_fitness_platform.zip explainable_ar_fitness_platform -x "*/node_modules/*" "*/.venv/*"
