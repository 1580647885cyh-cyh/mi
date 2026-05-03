.PHONY: run test demo

run:
	uvicorn backend.app:app --reload --port 8000

test:
	python -m pytest tests

demo:
	python cli.py --input scripts/demo_payload.json --output run_result.json
