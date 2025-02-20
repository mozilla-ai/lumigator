# Using Lumigator UI
Lumigator comes with a web-based UI that allows you to interact with the Lumigator API. It is designed to be easy to use and to provide a quick way to get started with Lumigator.

## Getting Started
Follow the [quickstart](quickstart.md) to get Lumigator up and running. The UI can then be accessed by visiting [localhost](http://localhost) on your web browser. You should be able to see a screen with the sections **Datasets** and **Experiments**. Lets go through each of them in detail.

## Upload a Dataset
The main purpose of Lumigator is to help you select the model that works best for your particular data, amongst several available. It does this by evaluating multiple models on a sample of your data: your dataset.

The first step is to upload your dataset. This can be done by clicking on the **Provide Dataset** button in the **Datasets** section. This will open a dialog box where you can select the dataset file to be uploaded from your local machine. The dataset file should be in `csv` format with columns examples and (optionally) ground_truth.

You can get started by uploading the {{ '[sample dataset](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/sample_data/dialogsum_exc.csv)'.format(commit_id) }} provided in the [Lumigator repository](https://github.com/mozilla-ai/lumigator).

![Datasets Page](../../assets/ui_guide_steps/datasets_page.png)

Once the dataset is uploaded, it can be viewed as a row in the table in the **Datasets** section.

![Datasets Table](../../assets/ui_guide_steps/datasets_table.png)

## Create and Run an Experiment
Next we move on to the **Experiments** section. Start by clicking on the **Create Experiment** button.

![Experiments Page](../../assets/ui_guide_steps/experiments_page.png)

This will open a sidebar where you would specify which use case and dataset, and further experiment details. The maximum samples field defines the number of rows from the dataset to be used for the experiment, on which Lumigator would run inference and evaluation to produce as results the [relevant metrics](quickstart.md#get-the-results).

Below that, you have the option to select the models to be used for the experiment. Multiple models may be simultaneously selected.

| ![Experiment Fields](../../assets/ui_guide_steps/experiment_fields.png) | ![Model Selection](../../assets/ui_guide_steps/model_select.png) |
| --- | --- |

```{note}
Reminder: In order to be able to use API based models, you must have provided the respective API keys (`OPENAI_API_KEY` or `MISTRAL_API_KEY`) as environment variables before starting Lumigator. See more in the [quickstart](quickstart.md).
```

Finally click the **Run Experiment** button.

![Experiments Running](../../assets/ui_guide_steps/experiments_running.png)

The **Experiments** page gets populated with the experiment details and the status of the experiment, which would initially be `RUNNING` and changes to `SUCCEEDED` once the experiment is complete or `FAILED` if the experiment fails.

![Experiments Completed](../../assets/ui_guide_steps/experiments_completed.png)

## View Results
For each experiment, you can view the sidebar which contains a **View Results** button. On clicking this button, we would be able to see a table with evaluation metrics comparing the previously selected models.

![Results Overall Comparison](../../assets/ui_guide_steps/results_overall_comparison.png)

You can further view the row by row predictions for each individual model by expanding under a given model. This gives you a detailed view of how the model predictions compare to the ground truth for each instance in the dataset.

![Results Row by Row Comparison](../../assets/ui_guide_steps/results_row_by_row.png)

---

Congratulations! With that, you have successfully run your first experiment using the Lumigator UI! You can continue to run more experiments by uploading your custom datasets and selecting from among the different models available.
