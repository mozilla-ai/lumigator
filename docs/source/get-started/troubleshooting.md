# Troubleshooting

This section describes some common issues and how you can solve them.
If the problem you are experiencing is not listed here, feel free to
[browse the list of open issues](https://github.com/mozilla-ai/lumigator/issues)
to check if it has already been discussed or otherwise open a
[bug report](https://github.com/mozilla-ai/lumigator/issues/new?template=bug_report.yaml).

## Could not install packages due to an OSError: [Errno 28] No space left on device

This problem usually occurs when the disk space allocated by Docker is completely
filled up. There are two ways to tackle this:

- increase the amount of disk space avaiable to the docker engine. You can do it
by opening Settings in Docker Desktop, opening the `Resources` section, and then
increasing the value specified under `Disk usage limit`

- you can remove the Docker images left dangling by our build process by running the
`docker image prune` command on the command line.
