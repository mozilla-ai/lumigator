# Running Lumigator Locally with Docker-Compose

You can run and develop Lumigator locally using `docker-compose` (follow the instructions under ["Get Started" here](../README.md)).
This creates four container services networked together to make up all the components of the Lumigator application:

- `postgres`, SQL database holding metadata for datasets and experiments.
- `localstack`, local storage for datasets that mimics S3-API compatible functionality. 
- `backend`, Lumigator’s FastAPI REST API.
- `ray`, a Ray cluster for submitting lm-buddy jobs and serving Ray Serve.

`docker-compose` automatically creates a network between these four containers.

Despite the fact this is a local setup, it lends itself to more distributed scenarios: e.g. one could provide different `AWS_*` env vars to the backend container to connect to any provider's S3-compatible service instead of localstack, a different `RAY_HEAD_NODE_HOST` to move compute to a remote ray cluster, and so on.


## Testing the services

 - `postgres` -  You can connect to it with any SQL client (e.g. pgAdmin) using localhost:5432 as its address,  `uname=admin` and `password=password`
 - `localstack` - You can test your localstack setup as follows:
   - `brew install peak/tap/s5cmd`
   - add the following to `~/.zshrc` and source it, or directly run the following commands:
        ```bash
        export AWS_ACCESS_KEY_ID=test
        export AWS_SECRET_ACCESS_KEY=test
        export AWS_DEFAULT_REGION=us-east-2
        export AWS_ENDPOINT_URL=http://localhost:4566
        alias s5='s5cmd --endpoint-url $AWS_ENDPOINT_URL'
       ```
    - Check out the storage: `s5 ls`
    - Check out the lumigator bucket: `s5 ls s3://lumigator-storage` (this will be created only after some action is performed on S3, e.g. uploading a dataset)
 - `backend` - You can directly connect to its [OpenAPI spec at localhost](http://localhost/docs#), see the available endpoints, and interactively run commands.
 - `ray` - You can connect to its dashboard [via HTTP to this address](http://localhost:8265/), see the cluster status, running jobs, their logs, etc. 

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
