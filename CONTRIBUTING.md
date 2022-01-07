### Development summary (+suggestions)
You will need a python environment (3.6 <= VERSION <= 3.10)

You will need pip installed

You will need [pre-commit](https://pypi.org/project/pre-commit/) `pip install pre-commit` installed.

You will need pip-tools `pip install pip-tools` installed.

```
pip-compile requirements/dev.in -o requirements/dev.txt
pip install -r requirements/dev.txt

pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

When making changes to any of the `requirements/*.in` files, you may run `pip-compile requirements/dev.in -o requirements/dev.txt` (or substitute `dev` for any of the other files) to recompile them. After doing so running `pip-sync requirements/dev.txt` (or substitute `dev` for any of the other files) will sync your environment with pip.

Additionally running `tox` should use your current version of python and attempt to run the above and any other tests / validation

#### Suggestion
use [conventional-commit](https://www.conventionalcommits.org/en/v1.0.0/) style

[gitcommit](https://www.conventionalcommits.org/en/v1.0.0/) provides a `gitcommit` cli that is quite decent.


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
# For older version compatibility
cp ~/.config/direnv/direnv.toml ~/.config/direnv/config.toml
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
direnv allow # if you have not whitelisted the path
direnv reload
```

##### Change python version (annoyingly required a reload)
```bash
export PYTHON_VERSION=3.9.9
direnv allow # if you have not whitelisted the path
direnv reload
```

##### Note in this version we install python (3.6.15 3.7.12 3.8.12 3.9.9 3.10.1) by default with pyenv

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

### PyCharm development

#### Needs PyCharm Professional edition (for ssh remote dev feature)
Setup project as remote ssh into the remote project directory

In a terminal (pycharm or not) create the virtual environments you want and pip-compile | install requirements txt

##### Add interpreters (under Project...remote...)
Virtualenv environment > Existing environment > select an appropriate one or 2 intepreters

Add `requirements/dev.txt` to Tools > Python Integrated Tools > Package requirements file
