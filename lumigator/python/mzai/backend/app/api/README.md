# Creating a new Lumigator endpoint

This document shows how current endpoints in lumigator work and describes the process needed to create a new one.
If you want to customize lumigator with your own custom endpoints / jobs this is a good place to start!

## Lumigator's architecture

The diagram below shows the current architecture of Lumigator. The larger
containers (UI, Backend, Ray cluster, DB, Storage) are the different services Lumigator relies on (for more info, check
[Running Lumigator Locally with Docker-Compose](https://github.com/mozilla-ai/lumigator/blob/main/.devcontainer/README.md)).

<p style="text-align: center;">
<img src="/docs/assets/platform.png" alt="Lumigator's architecture" >
Lumigator's architecture
</p>

The components inside Backend, shown in the image below, are the different abstraction layers the backend itself relies on:

* The **API** makes backend functionalities available to the UI (or whatever front-end you want to develop) through
  different **routes** (code
  [here](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/api/routes)).
  [**Schemas**](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/schemas) are used in the API
  which allows one to exactly know which kind of data has to be passed to it (similarly, using the same schemas will be
  a requirement for our SDK).

* **Services** implement the actual functionalities and are called by the different methods exposed in the API (code
  [here](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/services)).

* **Repositories** implement the [repository pattern](https://www.cosmicpython.com/book/chapter_02_repository.html) as
  an abstraction over the DB (code
  [here](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/repositories)). They make use
  of [record classes](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/records) to refer
  to actual records on the DB.

<p style="text-align: center;">
<img src="/docs/assets/backend_architecture.jpg" alt="Lumigator's backend" >
Lumigator's backend
</p>

## Notation

In the following, we will refer to paths inside Lumigator's repo relative to the `/lumigator/python/mzai` folder, e.g.
the relative path `backend/api/routes/` (note the lack of a trailing slash) will map to the absolute path from the root
of the repo `/lumigator/python/mzai/backend/api/routes/`.

## Understanding Lumigator endpoints

All the endpoints you can access in Lumigator's API are defined in
[`backend/api/routes/`](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/api/routes)
and explicitly listed in
[`backend/api/router.py`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/api/router.py),
together with a metadata tag (defined
[here](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/api/tags.py)) which is used to
provide a short description of the route:

<p style="text-align: center;">
<img src="/docs/assets/routes_definition.png" alt="Definition of the current routes in Lumigator" >
Definition of the current routes in Lumigator
</p>

<p style="text-align: center;">
<img src="/docs/assets/tags_definition.png" alt="Description tag for the Health endpoint" >
Description tag for the Health endpoint
</p>

<p style="text-align: center;">
<img src="/docs/assets/health_api_descr.png" alt="Description appearing in the API docs" >
Description appearing in the API docs
</p>

### The simplest endpoint: /health

The [`/health`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/api/routes/health.py) route provides
perhaps the simplest example as it allows you to get the current backend status which is a constant:

```
@router.get("/")
def get_health() -> HealthResponse:
    return HealthResponse(deployment_type=settings.DEPLOYMENT_TYPE, status="OK")
```

Note that the returned type is a `HealthResponse`: this is a
[pydantic model](https://docs.pydantic.dev/latest/api/base_model/) defining the schema of the returned data. The general
rule is that all return values in our routes should match a predefined schema. Schemas are defined under the `schemas`
folder (in particular, `HealthResponse` can be found
[here](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/schemas/extras.py)), typically in files
with the same name of the route, service, etc.

Being this simple, all the code for `get_health()` directly appears in the route file. A `HealthResponse`, composed of a
deployment type which is loaded from 
[`backend/settings.py`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/settings.py) and the status (currently always ok), is returned. Nothing is ran, nothing is saved on DB or on storage.

### One step further: /datasets

The `/datasets` route is a bit more complex as it has to interface both with the DB and the storage. The simplest method
there, `get_dataset`, already has basically all the components you'd find in most of the advanced methods:

```
@router.get("/{dataset_id}")
def get_dataset(service: DatasetServiceDep, dataset_id: UUID) -> DatasetResponse:
    return service.get_dataset(dataset_id)
```

* the core functionalities are provided by a *service* (in this case a `DatasetService`) defined in
  [`backend/services/datasets.py`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/services/datasets.py)

* instead of directly passing a `DatasetService` to the `get_dataset` method, DatasetServiceDep is defined to perform a
  *dependency injection* (see [FastAPI's dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/))

* as with the `/health` endpoint, a *schema* defines the return type (in this case a `DatasetResponse`)

* even if you don't see it yet, one more abstraction (*repository*) is used to access data on the DB

So, let us suppose you have already uploaded a dataset on Lumigator. What happens when you hit the
`/datasets` endpoint by passing a dataset id?

First thing, `DatasetServiceDep` will make sure that all the dependencies to run your `DatasetService` are met. If you
look at [`backend/api/deps.py`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/api/deps.py) you will see that
a `DatasetServiceDep` is nothing more than a `DatasetService` that depends on a `DBSessionDep` and and `S3ClientDep`:

```
DatasetServiceDep = Annotated[DatasetService, Depends(get_dataset_service)]

def get_dataset_service(session: DBSessionDep, s3_client: S3ClientDep) -> DatasetService:
    dataset_repo = DatasetRepository(session)
    return DatasetService(dataset_repo, s3_client)
```

`DBSessionDep` and and `S3ClientDep` provide and additional level of dependencies, namely on a database session and on
an S3 client.  
I'll leave you to transitively following deps. For now, it is interesting to note that while the S3 dep is a "simple"
one (i.e. it just instantiates a boto3 client in place), the DB one is a bit more advanced (i.e. it relies on a
[`DatabaseSessionManager`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/db.py) to return a session).

Secondly, `DatasetService` provides a `get_dataset` method which gets the actual data from the DB and returns a
`DatasetResponse` after validating it:

```
def get_dataset(self, dataset_id: UUID) -> DatasetResponse:
    record = self._get_dataset_record(dataset_id)
    return DatasetResponse.model_validate(record) 
        
def _get_dataset_record(self, dataset_id: UUID) -> DatasetRecord:
    record = self.dataset_repo.get(dataset_id)

    if record is None:
        self._raise_not_found(dataset_id)
    return record
```

The way data is selected from the DB is through a *repository* , in this case from the `DatasetRepository` class. All
repositories are defined in `backend/repositories` and inherit from 
[`BaseRepository`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/repositories/base.py) which is
a general class providing the low-level code to count, create, update, get, delete, and list items. In particular, the
`DatasetRepository` is a `BaseRepository` working with items of type
[`DatasetRecord`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/records/datasets.py).

Fields in records are defined as a mix of explicit type definitions and declarative mappings (see the picture below to
see how the fields in the datasets table are defined).


<p style="text-align: center;">
<img src="/docs/assets/records_inheritance.jpg" alt="Definition of the fields appearing in DatasetRecord" >
Definition of the fields appearing in DatasetRecord
</p>


<p style="text-align: center;">
<img src="/docs/assets/table_schema.png" alt="Table schema on the DB" >
Table schema on the DB
</p>


## Common patterns

The examples above show the main patterns we follow to develop a generic endpoint. These are reflected in a rather
standard code structure:

|                        |                                                                                                                                                                                                                                           |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`backend/api/routes`](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/api/routes)   | The actual API endpoints one can hit (remember they need to be explicitly added to the [router.py](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/api/router.py) file before you can actually see them!) |
| [`backend/services`](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/services)     | The code that implements core functionalities for each route                                                                                                                                                                              |
| [`backend/api/deps.py`](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/api/deps.py)  | Used to inject dependencies for services                                                                                                                                                                                                  |
| [`schemas`](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/schemas)              | The schemas used by each route / service                                                                                                                                                                                                  |
| [`backend/repositories`](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/repositories) | Repositories used by each service                                                                                                                                                                                                         |
| [`backend/records`](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/records)      | Records used by each service                                                                                                                                                                                                              |

The general rule is that for most endpoints you'll end up with an identical filename for each of the above directories
(see e.g. `datasets`, `experiments`, `groundtruth`, etc).

## Writing a new endpoint

The examples above show the main pieces of code involved in writing a new endpoint. Let us take a toy example, which is
creating an endpoint which given a task in the form of a string (e.g. "summarization") will return a list of model names
(string URIs) to be evaluated for that task. As you do not have a table with this information in our DB yet, you will
also create a method to actually *save* this list in a table.

### Step 1: Create a static endpoint

As a first step, you'll create a static endpoint which, regardless of the input, will always return the same list of
models. This is a good way to start as it allows you to wire the endpoint, see it in the docs, and make sure its schema
is correct, without the need to access the DB yet.

#### 1.1. Write the router code

The following code implements a barebone version of our endpoint, one which does not require any connection to the DB
nor a specific schema definition. It defines one method `get_model_list` that always returns a `ListingResponse[str]`
object, basically a dictionary containing a list of `items` of a predefined type (strings in our case) and a `total`
field with the number of items. Note that `task_id` is not even used, but this will change as soon as we want to get a
list which is task-specific.

```
from fastapi import APIRouter
from schemas.extras import ListingResponse

router = APIRouter()

@router.get("/{task_id}/models")
def get_model_list(task_id: str) -> ListingResponse[str]:
    """Get list of models for a given task."""
    return_data = {
        "total": 3,
        "items": [
            "hf://facebook/bart-large-cnn",
            "mistral://open-mistral-7b",
            "oai://gpt-4-turbo",
        ],
    }
    return ListingResponse[str].model_validate(return_data)
```

Being this the code for a new route, you will save it in `backend/api/routes/tasks.py`.

#### 1.2. Add the route to `router.py`with the appropriate tags

The following step is adding the new route to [`backend/api/router.py`](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/api/router.py). The code below shows the updated file with
comments next to the two lines marked below as **NEW**:

```
from fastapi import APIRouter

from mzai.backend.api.routes import (
    completions,
    datasets,
    experiments,
    groundtruth,
    health,
    tasks, ### NEW
)
from mzai.backend.api.tags import Tags

API_V1_PREFIX = "/api/v1"

api_router = APIRouter(prefix=API_V1_PREFIX)
api_router.include_router(health.router, prefix="/health", tags=[Tags.HEALTH])
api_router.include_router(datasets.router, prefix="/datasets", tags=[Tags.DATASETS])
api_router.include_router(experiments.router, prefix="/experiments", tags=[Tags.EXPERIMENTS])
api_router.include_router(groundtruth.router, prefix="/ground-truth", tags=[Tags.GROUNDTRUTH])
api_router.include_router(completions.router, prefix="/completions", tags=[Tags.COMPLETIONS])
api_router.include_router(tasks.router, prefix="/tasks", tags=[Tags.TASKS]) ### NEW
```

Also note that we are specifying some `Tags.TASKS` which have not been defined yet! Open [`backend/api/tags.py`](https://github.com/mozilla-ai/lumigator/tree/main/lumigator/python/mzai/backend/api/tags.py) and add
the sections marked below as **NEW**:

```
from enum import Enum


class Tags(str, Enum):
    HEALTH = "health"
    DATASETS = "datasets"
    EXPERIMENTS = "experiments"
    GROUNDTRUTH = "groundtruth"
    COMPLETIONS = "completions"
    TASKS = "tasks" ### NEW


TAGS_METADATA = [
    {
        "name": Tags.HEALTH,
        "description": "Health check for the application.",
    },
    {
        "name": Tags.DATASETS,
        "description": "Upload and download datasets.",
    },
    {
        "name": Tags.EXPERIMENTS,
        "description": "Create and manage evaluation experiments.",
    },
    {
        "name": Tags.GROUNDTRUTH,
        "description": "Create and manage ground truth generation",
    },
    {
        "name": Tags.COMPLETIONS,
        "description": "Access models via external vendor endpoints",
    },
    ### NEW TAGS BELOW
    {
        "name": Tags.TASKS,
        "description": "Mapping model lists to tasks.",
    },
]
```

#### 1.3. Test

Connect to [http://localhost/docs](http://localhost/docs) and you should see the following:

<p style="text-align: center;">
<img src="/docs/assets/tasks_api_descr.png" alt="Your newly created tasks endpoint" >
Your newly created tasks endpoint
</p>

If you click on `Try it out`, add any value for `task_id` and then click on `Execute` you should get the following
response:

<p style="text-align: center;">
<img src="/docs/assets/tasks_response.png" alt="Example response from the tasks endpoint" >
Example response from the tasks endpoint
</p>


### Step 2: Wire the endpoint to the DB

You have a new running endpoint! Too bad it always return the same identical data... Let's fix this by connecting it to
the DB.

#### 2.2. Define schema

To have a more useful endpoint, let us first update the schema with a few additional fields. The following goes
into`schemas/tasks.py`:

```
import datetime
from uuid import UUID

from pydantic import BaseModel


class TaskCreate(BaseModel):
    name: str
    description: str = ""
    models: list[str]


class TaskResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    created_at: datetime.datetime
    models: list[str]
```

If you look at `TaskResponse`, you can see that we added an `id` to uniquely identify the task, a `name` that we can
show e.g. in a list for users to choose from and a `description`. The field `created_at` will be automatically filled
when creating a new record. The list of `models` still appears, but we removed the count as we'll likely provide short
lists and we can expect to be able to get their length programmatically.

The `TaskCreate` class, instead, will be used to define the input to the `create_task` method in the API (the fields
`id` and `created_at` are not necessary, as they'll be created automatically by the DB).

#### 2.2. Define repositories and records

The code for a new repository (to be stored in `backend/repositories/tasks.py`) is quite standard:

```
from sqlalchemy.orm import Session

from mzai.backend.records.tasks import TaskRecord
from mzai.backend.repositories.base import BaseRepository


class TaskRepository(BaseRepository[TaskRecord]):
    def __init__(self, session: Session):
        super().__init__(TaskRecord, session)
```

This does not usually change much as long as you are fine with the base methods provided by the
[`BaseRepository`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/repositories/base.py) class.

The `TaskRepository` is a repository that allows to run the set of methods defined in the `BaseRepository` on the table
defined by `TaskRecord`. You can define a `TaskRecord` in `backend/records/tasks.py` as follows:

```
from sqlalchemy.orm import Mapped, mapped_column

from mzai.backend.records.base import BaseRecord
from mzai.backend.records.mixins import CreatedAtMixin, NameDescriptionMixin


class TaskRecord(BaseRecord, NameDescriptionMixin, CreatedAtMixin):
    __tablename__ = "tasks"
    models: Mapped[list[str]] = mapped_column(nullable=False)
```

Similarly to what you saw before for `DatasetRecord`, `TaskRecord` inherits from
[`BaseRecord`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/records/base.py) the property
of having an `id` primary key. In addition to that, it inherits `name` and `description` from `NameDescriptionMixin` and
`created_at` from `CreatedAtMixin`. The only field that we need to specify manually is `models`, a non-null column
holding a list of strings.

As SQLAlchemy does not have a built-in mapping from `list[str]`, you also need to update `BaseRecord` to provide one
explicitly by changing the following

```
type_annotation_map = {dict[str, Any]}
```

to

```
type_annotation_map = {dict[str, Any]: JSON, list[str]: JSON}
```

#### 2.3. Save DB-accessing methods into a TasksService

Now that you have an abstraction for the `tasks` table, you can use it to implement the different methods needed to
manage tasks. You'll do it inside `backend/services/tasks.py`:

```
from uuid import UUID

from fastapi import HTTPException, status

from app.records.tasks import TaskRecord
from app.repositories.tasks import TaskRepository
from schemas.extras import ListingResponse
from schemas.tasks import TaskCreate, TaskResponse


class TaskService:
    def __init__(self, tasks_repo: TaskRepository):
        self.tasks_repo = tasks_repo

    def _raise_not_found(self, task_id: UUID) -> None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Task '{task_id}' not found.")

    def _get_task_record(self, task_id: UUID) -> TaskRecord:
        record = self.tasks_repo.get(task_id)

        if record is None:
            self._raise_not_found(task_id)
        return record

    def get_task(self, task_id: UUID) -> TaskResponse:
        record = self._get_task_record(task_id)
        return TaskResponse.model_validate(record)

    def create_task(self, request: TaskCreate) -> TaskResponse:
        # Create DB record
        record = self.tasks_repo.create(
            name=request.name, description=request.description, models=request.models
        )
        return TaskResponse.model_validate(record)

    def delete_task(self, task_id: UUID) -> None:
        record = self._get_task_record(task_id)
        # Delete DB record
        self.tasks_repo.delete(record.id)

    def list_tasks(self, skip: int = 0, limit: int = 100) -> ListingResponse[TaskResponse]:
        total = self.tasks_repo.count()
        records = self.tasks_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[TaskResponse.model_validate(x) for x in records],
        )
```

The main methods implemented here are:

* `create_task`: uses the `create` method in the task repository (a method inherited by `BaseRepository`) to save a new
  task record. The `request` input parameter is defined in the `TaskCreate` schema and the output is a `TaskResponse`.

* `delete_task`: given a task `UUID`, deletes the corresponding record from the table. Note that, as all the other
  methods that rely on `_get_task_record`, an HTTP 404 exception is thrown if a matching record is not found in the
  table.

* `get_task`: given a task `UUID`, return the corresponding record (as a `TaskResponse`)

* `list_tasks`: returns a `ListingResponse` of `TaskResponse` elements (i.e. a list of tasks stored in the table).

Note how similar this is to some of the other services (e.g. `DatasetService`): you can expect this from services which
only deal with the DB as the main operations you'll do are those who operate on a table (create, delete, get, list,
etc). You will likely see a different behavior in more advanced endpoints (e.g. those which involve running ray jobs),
but we'll discuss that in another tutorial.

#### 2.4. Inject dependencies into a TaskService

As `TaskService` depends on the existence of a database, we should inject a dependency on a DB session. To do this, add
the following code to 
[`backend/api/deps.py`](https://github.com/mozilla-ai/lumigator/blob/main/lumigator/python/mzai/backend/api/deps.py):

```
def get_task_service(session: DBSessionDep) -> TaskService:
    task_repo = TaskRepository(session)
    return TaskService(task_repo)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
```

#### 2.5. Update routes

You are almost there! The last thing you need to do is update the `backend/api/routes/tasks.py`file with new code which
will map API requests to `TaskService` methods:

```
from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import TaskServiceDep
from schemas.extras import ListingResponse
from schemas.tasks import TaskCreate, TaskResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(service: TaskServiceDep, request: TaskCreate) -> TaskResponse:
    return service.create_task(request)


@router.get("/{task_id}")
def get_task(service: TaskServiceDep, task_id: UUID) -> TaskResponse:
    return service.get_task(task_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(service: TaskServiceDep, task_id: UUID) -> None:
    service.delete_task(task_id)


@router.get("/")
def list_tasks(
    service: TaskServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[TaskResponse]:
    return service.list_tasks(skip, limit)
```

#### 2.6. Test

To test your new endpoint, connect to [http://localhost/docs](http://localhost/docs) (you can find instructions for setting up local testing [here](https://docs.google.com/document/d/1ykFlD71QPa9OGNG_G0T9GCWePBhT6jRYlEzInJ323Nw/edit)). 
You should see a new section like
the following one:

<p style="text-align: center;">
<img src="/docs/assets/tasks_api_methods.png" alt="List of new methods in the tasks endpoint" >
List of new methods in the tasks endpoint
</p>

Here is an example for the creation of a new task:

<p style="text-align: center;">
<img src="/docs/assets/tasks_api_new.png" alt="New task creation" >
New task creation
</p>

And here is the format of a task list (to which we have also added a `summarization_eval` task):

<p style="text-align: center;">
<img src="/docs/assets/tasks_api_list.png" alt="The current list of tasks on the system" >
The current list of tasks on the system
</p>


## Final checks and reference code

Creating a new endpoint in Lumigator requires some prior knowledge about the system and due to how the code is
structured you will have to edit many different files (see the picture below). Once you get the gist of it, though, the
task can be quite straightforward (albeit a bit repetitive), especially if the endpoint mostly has to deal with DB
operations.

<p style="text-align: center;">
<img src="/docs/assets/git_status.png" alt="The list of new and updated files for the tasks endpoint" >
The list of new and updated files for the tasks endpoint
</p>



You can find the code written for this tutorial in
[this branch](https://github.com/mozilla-ai/lumigator/tree/tutorials/create_new_endpoint).
