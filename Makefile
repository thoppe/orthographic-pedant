title  = "Orthographic Pedant"
author = "Travis Hoppe"
target = "HnT_orthographic_pedant.md"
html_target = "HnT_index.html"

python_exec    = python
md2reveal_exec = md2reveal/md2reveal.py

args = --html_title $(title) --html_author $(author) 

all:
	$(python_exec) $(md2reveal_exec) $(target) --output $(html_target) $(args)

edit:
	emacs $(target) &

commit:
	@-make push

check:
	find . -maxdepth 1 -name "*.md" -exec aspell check {} \;

view:
	chromium-browser $(html_target)

clean:
	rm -rvf index.html
	rm -rvf .render_cache/

#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=
# Build dependencies
#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=

build_deps:
	-git submodule add https://github.com/hakimel/reveal.js.git reveal.js
	-git submodule add https://github.com/thoppe/md2reveal.git md2reveal

	git submodule update --init
	cd reveal.js && git checkout v0.3-1438-g9a89e39 && cd ..
	cd md2reveal && git pull origin master && cd ..
	git submodule status
