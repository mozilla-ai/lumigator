# Lumigator API

## Uploading a dataset
Lumigator does not directly access data on your disk, but expects you to first import your data on its object storage and then saves experiment outputs in the same place. Localstack takes care of this abstraction by creating an S3-compatible local object storage on your disk, so you can seamlessly access data locally, on AWS, or on CoreWeave’s compatible S3 storage.

The simplest way you can test a dataset upload to the platform is by directly accessing the API at the [OpenAPI doc URL](http://localhost/docs). 
Expand the Upload dataset section, click on Try it out, provide a dataset (you can browse and get it from disk) and click on Execute. 
If everything works properly, you should be able to see a JSON response in the Response body section that contains fields such as id (the one you will use to refer to this dataset from now on), filename, format, and so on.
Your dataset is stored on Lumigator!

You can now perform different operations:
    + see if it appears in List datasets 
    + Get dataset and provide its UUID to get its metadata back

## Running an Experiment

For step-by-step details, see the [demo notebook.](/notebooks/walkthrough.ipynb) 
