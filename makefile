c-env:
	python3 -m venv .venv

active-linux:
	. .venv/bin/activate

active-windows:
	.venv\Scripts\activate

install:
	pip3 install -r requirements.txt

reset-db:
	rm -rf migrations
	python3 init_db.py

run:
	python3 run.py