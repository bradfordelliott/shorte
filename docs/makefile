help:
	@echo "Available Targets"
	@echo "================="
	@echo " Build:"
	@echo "   docs = Generate the user guide"

OUTPUT:=html
THEME:=shorte
TARGET:=./build-output

docs:
	../src/shorte -f user_guide.tpl -p "${OUTPUT}" -t "${THEME}" --output=${TARGET} --output_file=user_guide.html

pdf:
	../src/shorte.py -f user_guide.tpl -p "html+pdf" -t shorte

merge:
	../src/shorte.py -f user_guide.tpl -p "mergefile" -t cortina_public

publish:
	cp -r build-output/. ../../shorte_pages/shorte/.


