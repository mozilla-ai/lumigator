# Local development

You can run and develop Lumigator locally using `docker-compose`, which creates four container services networked together to make up all the components of the Lumigator application.

The four services are:

 - `postgres` - SQL database holding metadata for datasets and experiments
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
you can develop right within the Docker container and have the application immediately reflect the changes via
`CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80",  "--reload"]`

The main dockerfile is `Dockerfile.backend`, which ships the deployment code to the Ray cluster via a mounted volume, and the application itself,
which is shipped directly as a dir via Docker.

In order to use the API-based vendor ground truth generation and evaluation, you'll need to pass the following environment variables for credentials:
+ `MISTRAL_API_KEY`
+ `OPENAI_API_KEY`
into the docker container.
