### Docker

From the `docker` folder

#### Build container against an uploaded pypi kintro package

##### Required docker >= 18.09
`DOCKER_BUILDKIT=1 docker build --target kintro-pkg -t kintro --build-arg KINTRO_VERSION=0.0.1rc1 --build-arg PYTHON_VERSION=3.6.15 --build-arg PYTHON_BASE=alpine3.15 .`

#### Build container against an fork/branch
`docker build --target kintro-repo -t kintro --build-arg KINTRO_REPO=https://github.com/neckbeard-io/kintro.git --build-arg KINTRO_BRANCH=main --build-arg PYTHON_VERSION=3.6.15 --build-arg PYTHON_BASE=alpine3.15 .`


### setup.py|setup.cfg

`python setup.py sdist bdist_wheel`
