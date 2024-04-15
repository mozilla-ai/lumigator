

# How to do some things in this repo with Pants



## Dependencies

### adding a  third party package 

In Pants, dependencies are *added* in a location and *consumed* elsewhere.

This repo _currently_ has all the deps in `model_builder/3rdparty/python/pyproject.toml`. For most pacakges,
you can add it to that list directly, run `pants generate-lockfiles`, and be on your way. 

from there you can use that  package (`foo` in this example) in your project like:


```
python_library(
    dependencies=["model_builder/3rdparty/python:foo"],
)
```


