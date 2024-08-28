# Local development

You can run and develop Lumigator locally using `docker-compose`, which creates four container services networked together to make up all the components of the Lumigator application.

The four services:

 - `postgres` - Database using GUID
 - `localstack` - local storage for datasets that mimics S3-API compatible functionality
 - `backend` - the lumigator REST API
 - `ray` - a Ray cluster for submitting lm-buddy jobs and serving Ray Serve

`docker-compose` automatically creates a network between these four containers. To use it, run `make local-up` at
the root of the repo, which will spin up then access the OpenAPI spec at `127.0.0.1/docs` to see and test all the endpoints.

You can run `make local-down` to spin down the server. The code is automatically reloaded by mounting as a volume,

```yaml
    volumes:
      - ../:/mzai
```

so if you configure your IDE to do so,
you can develop right within the Docker container and have the application immediately reflect the changes.

The main dockerfile is `Dockerfile.backend`, which ships the deployment code to the Ray cluster, and the application itself,
which is bundled as a `pex` executable.
