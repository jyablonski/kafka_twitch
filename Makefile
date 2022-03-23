.PHONY: docker-run
docker-run:
	@docker-compose up -d

.PHONY: docker-down
docker-down:
	@docker-compose down
	
.PHONY: check-topics
check-topics:
	docker-compose exec kafka kafka-topics \
		--list \
		--bootstrap-server kafka:9092

.PHONY: check-stream
check-stream:
	docker-compose exec kafka kafka-console-consumer \
		--bootstrap-server kafka:9092 \
		--topic twitch-streams \
		--from-beginning