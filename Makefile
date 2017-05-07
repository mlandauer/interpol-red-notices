all: test

build:
	docker build --no-cache -t interpol-red-notices .

test: build
	docker run -v $(PWD)/data:/data -e DATA_PATH=/data \
		-e DATABASE_URI=sqlite:////data/data.sqlite \
		-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		interpol-red-notices

clean:
	rm -rf data
