# Abort on error
set -e

# Probably easiest to run from hoff-server dir in repo root
hoffserver_dir=$PWD
docker_dir=$hoffserver_dir/docker
run_dir=$hoffserver_dir/run
[[ -e docker-deploy.sh ]] || { echo >&2 "Run from hemelb-hoff/hoff-server"; exit 1; }

# Pull base images
docker image pull mariadb:10.3
docker image pull python:2.7.15-alpine3.8

# Build app image
docker image build -f $docker_dir/flask-app-image/Dockerfile -t hoff/server:latest $hoffserver_dir
docker image tag hoff/server:latest localhost:5000/hoff/server:latest
docker push localhost:5000/hoff/server:latest

mkdir -p $run_dir
cd $run_dir

# Create secrets
sh $docker_dir/init_secrets.sh

# copy configs
ln -s $docker_dir/production.conf hoffserver.conf
ln -s $docker_dir/gunicorn.conf
# link stack def
ln -s $docker_dir/stack-base.yml

stack_name=hoff
