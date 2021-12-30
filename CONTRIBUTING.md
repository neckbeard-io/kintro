### Virtualenv development
TODO

### Docker development
#### version + base
Choose a python version (ex: 3.6.15)
Choose a python container base (ex: alpine3.15)

```bash
pushd docker
docker build -f Dockerfile-dev --build-arg PYTHON_VERSION=3.6.15 --build-arg PYTHON_BASE=alpine3.15 -t kintro-dev .`
popd
```

#### Full override
Choose a python base container and python version (ex: 3.6 or 3.6.15)

```bash
pushd docker
docker build -f Dockerfile-dev --build-arg PYTHON_VERSION=3.6 --build-arg PYTHON_IMAGE=python:3.6.15-alpine3.15 -t kintro-dev .
popd
```

#### Run your container (default command is bash into the code directory you mounted in
```
mkdir -p .env_cache .cache
docker run --rm -it -v $(pwd):/kintro -v PATH_TO_SSH_FOLDER:/home/kintro/.ssh:ro -v .env_cache:/home/kintro/.envs -v .cache:/home/kintro/.cache -v PATH_TO_DATA_DIR:/data --user $(id -u):$(id -g) kintro-dev
```
