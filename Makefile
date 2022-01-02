.PHONY: all clean

MOCOBEER_DIR=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

all:
	$(MOCOBEER_DIR)generate_mocobeer_static.py -i $(MOCOBEER_DIR)mocobeer.json -o $(MOCOBEER_DIR)index.html -f

clean:
	$(RM) $(MOCOBEER_DIR)index.html
	
