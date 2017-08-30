.PHONY: docker docker-run docker-push

docker-build: 
	@docker build -t litl/leeroy .
    

docker-run: docker
	@docker-compose up && true

