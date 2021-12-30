### Virtualenv development (with pyenv and direnv)
##### Sources
###### https://stackabuse.com/managing-python-environments-with-direnv-and-pyenv/
###### https://ideas.offby1.net/posts/direnv-and-pip-tools-together.html
#### See for dependencies https://github.com/pyenv/pyenv/wiki#suggested-build-environment
```bash
curl -L https://pyenv.run | bash
```

#### Assuming ubuntu
```bash
sudo apt-get install direnv
```

#### Setup the configs
```bash
mkdir -p ~/.config/direnv
cp docker/direnvrc ~/.config/direnv/direnvrc
```

#### Optionally whitelist kintro for direnv
```bash
cat <<EOF > ~/.config/direnv/direnv.toml
[whitelist]
prefix = [ "FULL_PATH_TO_KINTRO_REPO" ]
EOF
```


#### Assuming bash
```bash
echo 'export PATH="~/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="~/.local/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(direnv hook zsh)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc
```

#### Replace with whatever version you want
```bash
export PYTHON_VERSION=3.6.15
direnv allow
```

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
```bash
mkdir -p .env_cache .cache
docker run \
        --rm \
        -it \
        -v \
        $(pwd):/kintro \
        -v /kintro/.direnv \
        -v ~/.ssh:/home/kintro/.ssh:ro \
        -v $(pwd)/.env_cache:/home/kintro/.envs \
        -v $(pwd)/.cache:/home/kintro/.cache \
        --user $(id -u):$(id -g) \
        kintro-dev
```
