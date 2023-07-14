
.PHONY: protos chassisprotos fixpackages

PROTOFILES:=$(shell find protos -name *.proto)

protos:
	make chassisprotos
	source .venv/bin/activate && \
	pip install build && \
	python -m build packages/chassisml-protobuf4 && \
	pip install --force-reinstall packages/chassisml-protobuf4/dist/chassisml_protobuf-4.0.0-py3-none-any.whl

chassisprotos:
	python3.9 -m venv packages/chassisml-protobuf3/.venv && \
	source packages/chassisml-protobuf3/.venv/bin/activate && \
	pip install -r packages/chassisml-protobuf3/requirements-dev.txt && \
	mkdir -p packages/chassisml-protobuf3/src/chassis/protos && \
	python -m grpc_tools.protoc \
		-Iprotos \
		--python_out=packages/chassisml-protobuf3/src \
		--grpclib_python_out=packages/chassisml-protobuf3/src \
		$(PROTOFILES) && \
	deactivate && \
	rm -rf packages/chassisml-protobuf3/.venv
	python3.9 -m venv packages/chassisml-protobuf4/.venv && \
	source packages/chassisml-protobuf4/.venv/bin/activate && \
	pip install -r packages/chassisml-protobuf4/requirements-dev.txt && \
	mkdir -p packages/chassisml-protobuf4/src/chassis/protos && \
	python -m grpc_tools.protoc \
		-Iprotos \
		--python_out=packages/chassisml-protobuf4/src \
		--pyi_out=packages/chassisml-protobuf4/src \
		--grpclib_python_out=packages/chassisml-protobuf4/src \
		$(PROTOFILES) && \
	deactivate && \
	rm -rf packages/chassisml-protobuf4/.venv
	#make fixpackages
	touch packages/chassisml-protobuf3/src/chassis/protos/__init__.py
	touch packages/chassisml-protobuf3/src/chassis/protos/v1/__init__.py
	touch packages/chassisml-protobuf4/src/chassis/protos/__init__.py
	touch packages/chassisml-protobuf4/src/chassis/protos/v1/__init__.py

#fixpackages:
#	find packages/chassisml-protobuf* -type f -name '*.py*' -exec sed -i '' -e '/^from chassis\.v\d import/ s/chassis\.v/chassisml.protos.chassis.v/g' -e '/^import chassis\.v\d+\./ s/chassis\.v/chassisml.protos.chassis.v/g' -e '/^from google\.api import/ s/google\.api/chassisml.protos.google.api/g' {} \;
