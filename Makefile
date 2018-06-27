
PHONY: install

all: ufo
P := ufo

classes := \
	campaign \
	campaign_item \
	product
#	click

ufos := $(addsuffix .php, $(classes) )
ufos := $(addprefix Output/$P_, $(ufos))

foo:
	echo $(ufos)

# don't generate since i've customized this.
#	ufo_object.php

ufo: $(ufos)

Output/$P_%.php: Input/%.ufo Templates/ufo_class.T Templates/ufo_class_base.T parseUfo.py UfoFilter.py
	./parseUfo.py $^

.PHONY: test
test:
	@export PYTHONPATH=`pwd` && Test/Test.py Test/Test.config Test/Test.T Test/Test.out
	@if diff Test/Test.out Test/Test.out.success ; then echo SUCCESS ; else echo FAILED; fi

install: ufo
	# cp $(ufos) ../www
