from paths import PathPrefix, strip_path_prefix


def resolve_model_repo(path: str) -> str:
    """Resolve an `AssetPath` to a loadable string path without the prefix.

    Args:
        path (str): The path to resolve.

    Returns:
        str: The resolved path.
    """
    if not path.startswith(PathPrefix.HUGGINGFACE):
        allowed_prefixes = {x.value for x in PathPrefix}
        raise ValueError(
            f"Unable to resolve asset path from {path}. Allowed prefixes: {allowed_prefixes}"
        )

    return strip_path_prefix(path)
