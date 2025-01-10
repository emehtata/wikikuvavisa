# Variables
NAME = wikikuvavisa
IMAGE_NAME = localhost:5000/$(NAME)
TAG = latest
BRANCH = $$(git rev-parse --abbrev-ref HEAD)
VERSION = $$(git describe)

# Build the Docker image
build:
	echo "version='$(VERSION)'" > app/__version__.py
	docker build -t $(IMAGE_NAME):$(TAG) .

# Push the Docker image to the repository
push:
	docker push $(IMAGE_NAME):$(TAG)
	docker tag $(IMAGE_NAME):$(TAG) $(IMAGE_NAME):$(BRANCH)
	docker tag $(IMAGE_NAME):$(BRANCH) $(IMAGE_NAME):$(VERSION)
	docker push $(IMAGE_NAME):$(BRANCH)
	docker push $(IMAGE_NAME):$(VERSION)

# Clean up dangling Docker images
clean:
	docker system prune -f

# Run the Docker container locally on port 5500
run:
	docker run -d -p 5500:5500 --name $(NAME) $(IMAGE_NAME):$(TAG)

# Stop the running container
stop:
	docker stop $(NAME)

# Remove the stopped container
rm: stop
	docker rm $(NAME)

install:
	helm upgrade --install $(NAME) chart -n $(NAME) --create-namespace

uninstall:
	helm uninstall $(NAME) -n $(NAME)
