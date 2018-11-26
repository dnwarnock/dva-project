docker-compose -f docker-compose.setup.yml up -d mongo
docker-compose -f docker-compose.setup.yml up backend
docker-compose -f docker-compose.setup.yml down