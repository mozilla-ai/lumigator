load("@rules_oci//oci:defs.bzl", "oci_image", "oci_push", "oci_tarball")
load("//containers:py_layers.bzl", "py_layers")

"""
two macros that help ease using the container targets.

They generate teh `oci_image`, `oci_tarball`, and `oci_push` targets for given input.
"""

def oci_container(name, tars = [], registry = None, repository = None, tags = [], **kwargs):
    """Wrapper around oci_image that splits the py_binary into layers, generating
    other relevant targets for the underling `oci_image`

    args:
        name: name of the target, which will be used as a REPO name by default.
        tars: layers for this iamge
        registry: <URL>/orgname style, e..g, 'index.docker.io/mzdotai'
        repository: repo name for this target; defaults to `name`
        tags: tags for this push
    """
    env = kwargs.get("env", None)
    if not env:
        kwargs["env"] = {"PATH": "/usr/local/bin:$PATH"}

    repository = name if repository == None else repository
    oci_image(
        name = name,
        tars = tars,
        **kwargs
    )
    repo_tags = ["{}:{}".format(repository, tag) for tag in tags]
    oci_tarball(
        name = "{name}.tarball".format(name = name),
        image = ":{name}".format(name = name),
        repo_tags = repo_tags,
    )

    oci_push(
        name = "{name}.push".format(name = name),
        image = ":{name}".format(name = name),
        remote_tags = tags,
        repository = "{registry}/{repository}".format(registry = registry, repository = repository),
    )

def py_oci_container(name, binary, tars = [], registry = None, repository = None, tags = [], **kwargs):
    """Wrapper around oci_image that splits the py_binary into layers, generating
    other relevant targets for the underling `oci_image`

    args:

        name: name of the target, which will be used as a REPO name by default.
        binary: python bin target
        tars: layers for this image
        registry: <URL>/orgname style, e..g, 'index.docker.io/mzdotai'
        repository: repo name for this target; defaults to `name`
        tags: tags for this push
    """
    env = kwargs.get("env", None)
    if not env:
        kwargs["env"] = {"PATH": "/usr/local/bin:$PATH"}
    repository = name if repository == None else repository
    oci_image(
        name = name,
        tars = tars + py_layers(name, binary),
        **kwargs
    )
    repo_tags = ["{}:{}".format(repository, tag) for tag in tags]
    oci_tarball(
        name = "{name}.tarball".format(name = name),
        image = ":{}".format(name),
        repo_tags = repo_tags,
    )

    oci_push(
        name = "{name}.push".format(name = name),
        image = ":{}".format(name),
        remote_tags = tags,
        repository = "{registry}/{repository}".format(registry = registry, repository = repository),
    )
