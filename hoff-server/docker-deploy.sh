. docker-env-init.sh

docker stack deploy -c stack-base.yml $stack_name

# Get the ID of the database container
db_container=`docker container ps -f label=com.docker.swarm.service.name=${stack_name}_db -q`

# Generate the initialisation SQL and pipe through to the DB server as DB root user
sh ../docker/mk_db_init.sh | docker container exec -i $db_container mysql -u root --password=$(cat db_root_password)

