docker run -p 5432:5432 --volume=postgres_data:/var/lib/postgresql/data --env-file=./.env_db --hostname=db postgres:12.4-alpine
