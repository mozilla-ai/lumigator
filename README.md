# MZAI Platform

Source code for the MZAI model builder platform.


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

show targets:

```bash
make show-all-major-targets
```

compile targets manually:

```bash
pants package <target>
pants package src/python/mzai/model_builder:model_builder
# docker image
pants package src/python/mzai/model_builder:mzai_backend
```


## Running locally with Docker Compose via pants

```bash
pants run model_builder:mzai_backend_up
# shutdown
pants run model_builder:mzai_backend_down
```




