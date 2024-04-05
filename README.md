# MZAI Platform

Source code for the MZAI Platform.


# Setup 

install pants:

```shell
brew install pants
pants --version  # start the daemon
```

setup:
```bash
cat ./pants_tools/macosx_14_pex_platform_tags.json | jq '.path = "'$(which python)'"' > ./pants_tools/macosx_14_pex_platform_tags.json


```

compile targets manually:

```bash
pants package <target>
pants package src/python/mzai/backend:backend
# docker image
pants package src/python/mzai/backend:mzai_backend
```


## Running locally with Docker Compose via pants

```bash
pants run src/infra/docker:mzai_backend_up
# shutdown
pants run src/infra/docker:mzai_backend_down
```




