. docker-env-init.sh
secrets="db_root_password
db_web_password
web_admin_password
flask_secret_key
flask_security_salt"

for secret in $secrets; do
    docker secret create $secret $secret
done

#docker config create hoffserver.conf hoffserver.conf

docker network create --attachable --driver overlay hoffnet

docker service create --hostname db --name db --network hoffnet --env MYSQL_ROOT_PASSWORD_FILE=/run/secrets/db_root_password --secret db_root_password --mount type=volume,source=db_data,destination=/var/lib/mysql mariadb:10.3

# Get the ID of the database container
db_container=`docker container ps -f label=com.docker.swarm.service.name=db -q`

sh ../docker/mk_db_init.sh | docker container exec -i $db_container mysql -u root --password=$(cat db_root_password)

#hoff_id=`docker container create -p 8000:8000 --hostname flask --network hoffnet -v $PWD:/hoffdata --env HOFFSERVER_CONFIG=/etc/hoffserver.conf hoffserver:latest gunicorn --workers 3 --bind 0.0.0.0:8000 -m 007 hoffserver.wsgi --daemon`
hoff_id=`docker container run -d -p 8000:8000 --hostname flask --network hoffnet -v $PWD:/hoffdata --env HOFFSERVER_CONFIG=/etc/hoffserver.conf hoffserver:latest sleep 100d`

mkdir -p secrets
for secret in db_web_password flask_secret_key flask_security_salt; do
    cp $secret secrets/
done
docker container cp secrets $hoff_id:/run/
docker container cp hoffserver.conf $hoff_id:/etc/hoffserver.conf


