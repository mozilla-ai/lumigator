class ParameterGroup:
    def __init__(self, name, python_resolve, default_environment, complete_platforms):
        self.name = name
        self.resolve = python_resolve
        self.environment = default_environment
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
    python_resolve="linux_cuda",
    default_environment="local_linux",
    complete_platforms=["//3rdparty/python:py311_linux_pex_platform_tags"],
)
LINUX_CPU = ParameterGroup(
    name="linux_cpu",
    python_resolve="linux_cpu",
    default_environment="local_linux",
    complete_platforms=["//3rdparty/python:py311_linux_pex_platform_tags"],
)
DARWIN = ParameterGroup(
    name="darwin",
    python_resolve="darwin",
    default_environment="local_darwin",
    complete_platforms=["//3rdparty/python:py311_macos_14_pex_platform_tags"],
)

p_groups = (LINUX_CUDA, LINUX_CPU, DARWIN)

LOCAL_LINUX = "local_linux"


def crossplatform_pex(unparametrized_deps: list = None, group_names=None, **kwargs):
    """Parmetrizes the pex binary deps according to the three platforms we
    might want to build for. By default, explicit deps are not parametrized automatically and
    must be manually done for now.
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

    merge = lambda x, y: {**x, **y}
    d = {}
    for dict_ in pgs:
        d = merge(d, dict_)

    d = merge({"name": _name}, d)
    d = merge(d, kwargs)

    pex_binary(**d)
