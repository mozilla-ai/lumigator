###
# here we set three basic parametrized groups for our
# three main platform / gpu sets - darwin, linux, and linux with cuda.
# consistency across these names helps pants resolve the deps correctly,
# as `parametrize sets up a generated target for a given source like
# <path>:app_pex_binary -> <path>:app_pex_binary@parametrize=<linux_cuda|linux_cpu|darwin
# the `resolve` field is specific to python targets - it's the lockfile for a given set of deps.
#
# this is _NOT_ optimal code and would love to sort out how to do more like ParamGroup(...) defined here to make the
# defaults settings a lot cleaner.

# Note that also this _has_ to be partially repeated from the root `BUILD.pants` file.
# Pants Macros are *not* available when setting up Environment targets.
# that code is explicitly copied into here for consistency, and hopefully a more elegant
# solution can be made in the future.


def merge_dicts(dict1, dict2):
    return {**dict1, **dict2}


class ParameterGroup:
    def __init__(self, name, resolve, environment, complete_platforms):
        self.name = name
        self.resolve = resolve
        self.environment = environment
        self.complete_platforms = complete_platforms

    def pex(self):
        pex_kwargs: dict = {
            "resolve": self.resolve,
            "environment": self.environment,
            "complete_platforms": self.complete_platforms,
        }
        return parametrize(self.name, **pex_kwargs)

    def python_sources(self):
        py_kwargs: dict = {"resolve": self.resolve}
        return parametrize(self.name, **py_kwargs)

    def python_tests(self):
        pytest_kwargs: dict = {"resolve": self.resolve, "environment": self.environment}
        return parametrize(self.name, **pytest_kwargs)


LINUX_CUDA = ParameterGroup(
    name="linux_cuda",
    resolve="linux_cuda",
    environment="local_linux",
    complete_platforms=["//3rdparty/python:py311_linux_pex_platform_tags"],
)
LINUX_CPU = ParameterGroup(
    name="linux_cpu",
    resolve="linux_cpu",
    environment="local_linux",
    complete_platforms=["//3rdparty/python:py311_linux_pex_platform_tags"],
)
DARWIN = ParameterGroup(
    name="darwin",
    resolve="darwin",
    environment="local_darwin",
    complete_platforms=["//3rdparty/python:py311_macos_14_pex_platform_tags"],
)

p_groups = (LINUX_CUDA, LINUX_CPU, DARWIN)

LOCAL_LINUX = "local_linux"


def crossplatform_pex(unparametrized_deps: list = None, group_names=None, **kwargs):
    """Parmetrizes the pex binary deps according to the three platforms we
    might want to build for. By default, explicit deps are not parametrized automatically and
    must be handled like this to make the parametrization work correctly.
    """
    if group_names is None:
        groups = p_groups
    else:
        groups = [g for g in p_groups if g.name in group_names]

    _name = kwargs.pop("name", None)
    if _name is None:
        return

    if len(unparametrized_deps) == 0:
        print("no deps!")
        return

    pgs = []
    for group in groups:
        pgs.append(
            parametrize(
                group.name,
                complete_platforms=group.complete_platforms,
                dependencies=[f"{dep}@parametrize={group.name}" for dep in unparametrized_deps],
                environment=group.environment,
                resolve=group.resolve,
            )
        )

    d = {}
    for dict_ in pgs:
        d = merge_dicts(d, dict_)

    d = merge_dicts({"name": _name}, d)
    d = merge_dicts(d, kwargs)

    # return the `pex_binary` target which will be visible to pants
    pex_binary(**d)
