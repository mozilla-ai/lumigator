# Lumigator Demo Notebooks
A collection of Jupyter notebooks and scripts showcasing Lumigator's functionalities. For installing Lumigator, see the main [README.md](README.md)

The notebook runs on Jupyter. If you don't yet have Jupter set up: 

1. create a new virtualenv for lumigator
2. `cd notebooks` # (assuming you were in the root directory of the repo)
3. `pip install -r requirements.txt`
4. `pip install jupyterlab` 
5. set up the environment so that both our backend and our ray cluster point to localhost and start jupyterlab:
```LUMIGATOR_SERVICE_HOST="localhost" RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR="localhost" jupyter-lab```

A new browser window will open pointing at your new jupyterlab. From there, open the walkthrough.ipynb file by clicking on it.


## Running through the notebook

The notebook currently has some references to dataset/job UUIDs which are stale. 
The easiest way to get started with an evaluation job is the following:

+ all cells until the Generating Data for Ground Truth Evaluation section are tested and working 
+ you can run the cell which shows information about the Thunderbird dataset after providing your dataset UUID

For the public version of this document, a good dataset you could use is knkarthick/dialogsum which contains some short dialogues summarized in the ground truth. You can do something like:
```python
dataset='knkarthick/dialogsum'
ds = load_dataset(dataset, split='validation')
ds = ds.remove_columns(["id", "topic"])
ds = ds.rename_column("dialogue", "examples")
ds = ds.rename_column("summary", "ground_truth")
dataset_name = "dialogsum_converted.csv"
ds.to_csv(dataset_name)
```
and then save it using our current “SDK” with

```python
r = ld.dataset_upload(dataset_name)
# show ds info
dataset_id = ld.get_resource_id(r)
```