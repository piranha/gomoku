run:
	python -m gomoku.main --dev

prod:
	python -m gomoku.main

test:
	python setup.py nosetests
