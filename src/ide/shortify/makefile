all:
	python sql/translate.py sql/settings.sql > tmp.sql
	rm -rf settings.db
	sqlite3 settings.db < tmp.sql 
	cp settings.db ../build-gringo-Desktop_Qt_5_2_1_clang_64bit-Debug/gringo.app/Contents/MacOS/.
