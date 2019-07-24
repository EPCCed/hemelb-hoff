docker service rm db
docker network rm hoffnet
# docker config rm hoffserver.conf
for secret in $secrets; do
    docker secret rm $secret
done
