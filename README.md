# Twitch Kafka Scraper

Project that scrapes twitch.tv Data via the Twitch Helix API and uses Kafka to setup real-time message processing to receive new updates & store them to a remote PostgreSQL Database.

Currently the consumer receives messages for 60 seconds, transforms them out of JSON and into a Pandas DataFrame, and then writes to SQL and exits out afterwards.  In a production scenario this Kafka -> Consumer -> Storage loop would be running indefinitely and storing the data in microbatches such as every 60s like in this scenario.