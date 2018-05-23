#This makefile is a way to document the many docker commands used to run the system.
#It also is a nice way to manage the dependency that a container must be built before it can be run
# and that any time setup.sh or Dockerfile changes it should be re-built.

SHELL := /bin/bash

#All variables that change between different developers or envirinments should be in this file,
# which shouldn't be checked into the git repository.
include make_env

#Always do the build step, since this is what bundles the new code with the container.
.PHONY: .build

#Format:  the target name, then a file whose modified date represents the last time we ran this:
build .build : Dockerfile setup.sh make_env Makefile
	docker build -q -t $(NS)/$(IMAGE_NAME):$(VERSION) . > /dev/null && touch .build

push:
	docker push $(NS)/$(IMAGE_NAME):$(VERSION)
	
shell: .build
	docker run --rm --name $(CONTAINER_NAME)-$(CONTAINER_INSTANCE) -i -t $(PORTS) $(VOLUMES) $(ENV) $(NS)/$(IMAGE_NAME):$(VERSION) /bin/bash

run: .build
	docker run --rm -it --name $(CONTAINER_NAME)-$(CONTAINER_INSTANCE) $(PORTS) $(VOLUMES) $(ENV) $(NS)/$(IMAGE_NAME):$(VERSION) $(RUN_CMD)

benchmark: .build
	docker run --rm -it --name $(CONTAINER_NAME)-$(CONTAINER_INSTANCE) $(VOLUMES) $(BENCHMARK_ENV) $(ENV) $(NS)/$(IMAGE_NAME):$(VERSION) $(BENCHMARK_CMD)

#Starts a pdb session running the benchmark:
benchmarkPdb: .build
	docker run --rm -it --name $(CONTAINER_NAME)-$(CONTAINER_INSTANCE) $(VOLUMES) $(BENCHMARK_ENV) $(ENV) $(NS)/$(IMAGE_NAME):$(VERSION) $(BENCHMARK_PDB_CMD)

start: .build
	docker run -d --name $(CONTAINER_NAME)-$(CONTAINER_INSTANCE) $(PORTS) $(VOLUMES) $(ENV) $(NS)/$(IMAGE_NAME):$(VERSION)

stop:
	docker stop $(CONTAINER_NAME)-$(CONTAINER_INSTANCE)

rm: 
	docker rm $(CONTAINER_NAME)-$(CONTAINER_INSTANCE)

release: .build
	make push -e VERSION=$(VERSION)
	
default: run

