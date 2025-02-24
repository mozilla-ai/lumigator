# Preparing your own evaluation dataset

If you need more information about what this is and why, check this page first.

This guide will walk you through the process of preparing your own evaluation dataset
for Lumigator to help see the differences in performance of multiple Language Models for your own use case, rather than a generic benchmark.

This guide will cover the format Lumigator expects, what to focus on when collecting appropriate content and, lastly, how to upload and check your resulting file is valid.

## Format

Lumigator expects a CSV file containing different columns depending on the use case. Currently:

* Summarization use case

Your CSV should contain `examples` and `ground_truth`. See an example [here](../../../lumigator/sample_data/dialogsum_exc.csv ).

* Translation use case

Here you will have a source language (that you translate from) and a target language (that you translate to).

Your CSV should contain `examples_$SRC_LAN` and `ground_truth_$TAR_LAN`.

In the column names below, please ensure you replace the placeholders `$SRC_LAN` and `$TAR_LAN` with [ISO 639 2-character language codes](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes).

## Content

To prepare the samples that will actually be part of your dataset, you must collect, curate and annotate.

### 1. Collect

If you already have a system running, whether it already uses Language Models to summarize or not, automatically save examples that go into that system If there are humans or a high-quality process that already summarizes or translates these examples, collect those output summaries together with the input text.


```{note}
Ensure you are legally allowed and have collected consent from your users to collect this data.
```


At the end of this step, that depending on your workflow may take anywhere between minutes and months, you should have a list of as many examples as possible of at least original texts from your domain.

#### How many do you need?

Unfortunately, there is no clear-cut answer to this. Not as many as if you were training or fine-tuning a model, but remember: the more examples, the more likely it is that a model score was not a fluke.

#### Example output

Ideally you will end up with a text file or a spreadsheet with dozens (or hundreds or thousands) of examples. Let's imagine you are building an app that summarizes patient history. Your examples might look like:

```
    Patient A: 58-year-old male with persistent cough and chest pain for 3 months. CT scan revealed a lung mass. Biopsy and immunohistochemistry confirmed non-small cell lung cancer. Treatment: Surgical resection followed by chemotherapy.

    Patient B: 42-year-old female with recurring headaches and vision changes. MRI showed a pituitary tumor. Endocrine tests and fine-needle aspiration confirmed a prolactinoma. Treatment: Dopamine agonist medication.

    Patient C: 67-year-old male with fatigue and unexplained weight loss. Blood tests revealed abnormal white blood cell count. Bone marrow biopsy and flow cytometry diagnosed chronic lymphocytic leukemia. Treatment: Watch and wait approach with regular monitoring.

    Patient D: 35-year-old female with abdominal pain and bloating. Ultrasound showed ovarian masses. Surgical biopsy and histopathology confirmed ovarian endometriosis. Treatment: Laparoscopic excision of endometrial tissue.

    Patient E: 50-year-old male with difficulty swallowing. Endoscopy revealed esophageal lesions. Biopsy and immunohistochemistry diagnosed Barrett's esophagus with high-grade dysplasia. Treatment: Endoscopic mucosal resection and radiofrequency ablation.

    Patient F: 29-year-old female with skin rashes and joint pain. Blood tests showed positive ANA. Skin biopsy and immunofluorescence confirmed systemic lupus erythematosus. Treatment: Hydroxychloroquine and low-dose corticosteroids.

    Patient G: 72-year-old male with memory loss and confusion. PET scan showed reduced glucose metabolism in specific brain regions. Cerebrospinal fluid analysis and genetic testing diagnosed Alzheimer's disease. Treatment: Cholinesterase inhibitors and memantine.

    Patient H: 45-year-old female with breast lump. Mammogram and ultrasound revealed suspicious mass. Core needle biopsy and HER2/hormone receptor testing diagnosed HER2-positive breast cancer. Treatment: Lumpectomy, radiation, and targeted therapy.

    Patient I: 60-year-old male with rectal bleeding. Colonoscopy showed colorectal polyps. Polypectomy and histopathological examination diagnosed adenomatous polyps with high-grade dysplasia. Treatment: Endoscopic mucosal resection and regular surveillance colonoscopies.

    Patient J: 38-year-old female with thyroid nodule. Ultrasound-guided fine-needle aspiration and cytology were inconclusive. Surgical biopsy and frozen section analysis during surgery diagnosed papillary thyroid carcinoma. Treatment: Total thyroidectomy followed by radioactive iodine therapy.

    Patient K: 38-year-old woman presented with a thyroid mass. Initial diagnostic attempts using ultrasound-directed thin-needle sampling and cell examination yielded ambiguous results. Definitive diagnosis of papillary thyroid cancer was achieved through surgical tissue extraction and rapid intraoperative pathological assessment. The patient underwent complete removal of the thyroid gland, followed by treatment with radioiodine.

    Patient L: 38-year-old woman with thyroid mass. Ultrasound-directed thin-needle sampling and cell examination were inconclusive, later surgical tissue extraction and rapid intraoperative pathological assessment. Diagnosis: papillary thyroid cancer. Treatment was complete removal of the thyroid gland, followed by radioiodine therapy.

```

Notice at this point we do not know what an ideal summary of this would be.


### 2. Curate

This is the most time-intensive phase. Summon all your domain knowledge: which of those examples are basically the same as others? A few slightly paraphrased examples will help expose models, but if your whole dataset is built over 1000 ways of saying the same thing, the evaluation may not be the best.

For example, continuing with the example above, notice how similar the last 3 examples are. You might decide that only 1 is representative enough. You might also want to leave Patient J and K, since it may be good to check that the model also understands longer form writing, as in Patient K.

Your outcome then would be the list as above, minus Patient L.


### What to consider while you are curating?

* Is your data representative of your domain in production?
    * Are typical lengths of text covered?
    Consider seeing the distribution of the texts you collected in step #1:
    * Is there good coverage of the vocabulary in your data? (E.g. does a percentage of your users employ very distinct abbreaviations the rest do not use?)
    * Is there any seasonality in your data?
    For example, in the patient information example above: could that group of people who use a specific vocabulary only come in during internships in the Summer? Were you collecting examples from those dates?
    * Are all your users represented in your data?
    Beware of only choosing samples from one or two of your users. You could find that the model you select fails miserably when, in production, it needs to work for everyone.
* Are there enough samples? See the comment above.
* Are you selecting examples of all difficulties?
Be careful not to only choose examples that are either easy or hard to summarize, you want examples of all types.
* Could you be cheating?
If your data was involved in the training or fine-tuning of any of the models you are evaluating, do make sure only new, unseen data is present in the evaluation dataset.
Following the exam analogy, allowing samples to be shared between training and evaluation is similar to slipping a student a list of right answers before the exam (learn more about data leakage here).
* Do you have quality ground truth?


### 3. Annotate (optional in Lumigator, but very strongly encouraged)

Ground truth (i.e. the ideal output of the task for each example, as imagined by a human expert) is crucial to evaluate an LLM. Lumigator allows you to upload a dataset with only the input column and later annotate the dataset with a high-quality Language Model, but nobody has vetted that LLM for your use case: we cannot guarantee it knows as much about your business as you do.

If you do have human experts who were able to go through the input data from step #2 and add their annotations, you should end up with a file with the same list of examples, plus the annotation after a comma. Such as the following content:


```
examples,ground_truth
"Patient A: 58-year-old male with persistent cough and chest pain for 3 months. CT scan revealed a lung mass. Biopsy and immunohistochemistry confirmed non-small cell lung cancer. Treatment: Surgical resection followed by chemotherapy.","58M, lung cancer diagnosed via CT and biopsy, treated with surgery and chemo."
"Patient B: 42-year-old female with recurring headaches and vision changes. MRI showed a pituitary tumor. Endocrine tests and fine-needle aspiration confirmed a prolactinoma. Treatment: Dopamine agonist medication.","42F, prolactinoma found through MRI and hormone tests, managed with medication."
"Patient C: 67-year-old male with fatigue and unexplained weight loss. Blood tests revealed abnormal white blood cell count. Bone marrow biopsy and flow cytometry diagnosed chronic lymphocytic leukemia. Treatment: Watch and wait approach with regular monitoring.","67M, CLL detected by blood work and bone marrow biopsy, under observation."
"Patient D: 35-year-old female with abdominal pain and bloating. Ultrasound showed ovarian masses. Surgical biopsy and histopathology confirmed ovarian endometriosis. Treatment: Laparoscopic excision of endometrial tissue.","35F, ovarian endometriosis found via ultrasound and biopsy, treated surgically."
"Patient E: 50-year-old male with difficulty swallowing. Endoscopy revealed esophageal lesions. Biopsy and immunohistochemistry diagnosed Barrett's esophagus with high-grade dysplasia. Treatment: Endoscopic mucosal resection and radiofrequency ablation.","50M, Barrett's esophagus with dysplasia detected by endoscopy and biopsy, treated endoscopically."
"Patient F: 29-year-old female with skin rashes and joint pain. Blood tests showed positive ANA. Skin biopsy and immunofluorescence confirmed systemic lupus erythematosus. Treatment: Hydroxychloroquine and low-dose corticosteroids.","29F, lupus diagnosed through blood tests and skin biopsy, treated with immunosuppressants."
"Patient G: 72-year-old male with memory loss and confusion. PET scan showed reduced glucose metabolism in specific brain regions. Cerebrospinal fluid analysis and genetic testing diagnosed Alzheimer's disease. Treatment: Cholinesterase inhibitors and memantine.","72M, Alzheimer's identified by PET scan and CSF analysis, managed with medication."
"Patient H: 45-year-old female with breast lump. Mammogram and ultrasound revealed suspicious mass. Core needle biopsy and HER2/hormone receptor testing diagnosed HER2-positive breast cancer. Treatment: Lumpectomy, radiation, and targeted therapy.","45F, HER2+ breast cancer found through imaging and biopsy, treated with surgery, radiation, and targeted drugs."
"Patient I: 60-year-old male with rectal bleeding. Colonoscopy showed colorectal polyps. Polypectomy and histopathological examination diagnosed adenomatous polyps with high-grade dysplasia. Treatment: Endoscopic mucosal resection and regular surveillance colonoscopies.","60M, high-risk colon polyps detected by colonoscopy and biopsy, treated with endoscopic removal and monitoring."
"Patient J: 38-year-old female with thyroid nodule. Ultrasound-guided fine-needle aspiration and cytology were inconclusive. Surgical biopsy and frozen section analysis during surgery diagnosed papillary thyroid carcinoma. Treatment: Total thyroidectomy followed by radioactive iodine therapy.","38F, thyroid cancer confirmed through surgical biopsy, treated with thyroidectomy and radioiodine."
"Patient K: 38-year-old woman presented with a thyroid mass. Initial diagnostic attempts using ultrasound-directed thin-needle sampling and cell examination yielded ambiguous results. Definitive diagnosis of papillary thyroid cancer was achieved through surgical tissue extraction and rapid intraoperative pathological assessment. The patient underwent complete removal of the thyroid gland, followed by treatment with radioiodine.","38F, thyroid cancer confirmed through surgical biopsy, treated with thyroidectomy and radioiodine."
```

## Validate your dataset file

Now that you have a dataset (let's assume it's `my_dataset.csv`), let's upload it to Lumigator and check everything is fine.

You can do this via the UI or, as below, via the SDK.


## What You'll Need

- A running instance of [Lumigator](../get-started/quickstart.md).

## Procedure

1. Install the Lumigator SDK:

    ```console
    user@host:~/lumigator$ uv pip install -e lumigator/sdk
    ```

1. Create a new Python file:

    ```console
    user@host:~/lumigator$ touch upload_dataset.py
    ```

1. Add the following code to `upload_dataset.py`:

    ```python
    import json
    import requests
    from lumigator_schemas import datasets
    from lumigator_sdk.lumigator import LumigatorClient

    HOST = "localhost"
    LUMIGATOR_PORT = 8000

    # Instantiate the Lumigator client
    lm_client = LumigatorClient(f"{HOST}:{LUMIGATOR_PORT}")

    # Upload the dataset
    dataset_path = "my_dataset.csv"
    dataset = lm_client.datasets.create_dataset(dataset=open(dataset_path, "rb"), format=datasets.DatasetFormat.JOB)

    # Check the dataset was correctly added
    url = f"http://{HOST}:{LUMIGATOR_PORT}/api/v1/datasets/{dataset.id}"
    response = requests.get(url=url)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve dataset: {response.text}")
    else:
        print("Dataset looking good!")
        results = response.json()
    ```

1. Run the script:

    ```console
    user@host:~/lumigator$ uv run python upload_dataset.py
    ```

## Verify

You should see a confirmation like:

```console
Dataset looking good!
{'id': '67a2a5eb-9b1e-4c53-b133-bd7685e7d389', 'filename': 'my_dataset.csv', 'format': 'job', 'size': 3992, 'ground_truth': True, 'run_id': None, 'generated': False, 'generated_by': None, 'created_at': '2025-02-24T16:11:36'}
```

## Next Steps

Congratulations! You have successfully created an evaluation dataset and uploaded it using the Lumigator SDK. You can now start comparing models with each other for your use case!
