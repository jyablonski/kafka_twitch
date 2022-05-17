-include $(shell curl -ssl -o .jacobs-makefile "https://raw.githubusercontent.com/jyablonski/python_aws/jacob/Makefile"; echo .jacobs-makefile)
# this means use curl to download a file from the internet using ssl and write an output file and call it .jacobs-makefile, and then run it afterwards.


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

.PHONY: create-venv2
create-venv2:
	pipenv install