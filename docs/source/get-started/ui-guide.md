# Using Lumigator UI
Lumigator comes with a web-based UI that allows you to interact with the Lumigator API. It is designed to be easy to use and to provide a quick way to get started with Lumigator.

## Getting Started
Following the [installation guide](../get-started/installation.md), get Lumigator up and running from the command line:
```console
user@host:~/lumigator$ make start-lumigator
```
The UI can then be accessed by visiting [localhost](http://localhost) on a web browser. You should be able to see a screen with the sections **Datasets** and **Experiments**. Lets go through each of them in detail.

## Upload a Dataset
The first step is to upload a dataset. This can be done by clicking on the **Provide Dataset** button in the **Datasets** section. This will open a dialog box where you can select the dataset file to be uploaded from your local machine. The dataset file should be in `csv` format with columns examples and (optionally) ground_truth.

![Datasets Page](../../assets/ui_guide_steps/datasets_page.png)

Once the dataset is uploaded, it can be viewed as a row in the table in the **Datasets** section.

![Datasets Table](../../assets/ui_guide_steps/datasets_table.png)

## Create and Run an Experiment


## View Results
