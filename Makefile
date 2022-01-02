.PHONY: all clean deploy

# Directory to deploy generated files to
DEPLOY_DIR?=/tmp
# Web server group
DEPLOY_GROUP?=www-data

# Directory containing code
MOCOBEER_DIR=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

all:
	$(MOCOBEER_DIR)generate_mocobeer_static.py -i $(MOCOBEER_DIR)mocobeer.json -o $(MOCOBEER_DIR)index.html -f

clean:
	$(RM) $(MOCOBEER_DIR)index.html

deploy:
	git archive main | tar -x -C $(DEPLOY_DIR)
	$(MAKE) -C $(DEPLOY_DIR) all
	$(RM) $(DEPLOY_DIR)/generate_mocobeer_static.py $(DEPLOY_DIR)/README.md $(DEPLOY_DIR)/mocobeer.json $(DEPLOY_DIR)/Makefile $(DEPLOY_DIR)/blank.json
	find $(DEPLOY_DIR) -type f -exec chmod 440 {} \;
	find $(DEPLOY_DIR) -type d -exec chmod 550 {} \;
	chgrp -R $(DEPLOY_GROUP) $(DEPLOY_DIR)
