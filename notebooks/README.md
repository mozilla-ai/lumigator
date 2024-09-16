# Lumigator Demo Notebooks
A collection of Jupyter notebooks and scripts showcasing Lumigator's functionalities. For installing Lumigator, see the main [README.md](README.md)

The notebook runs on Jupyter. If you don't yet have Jupyter set up: 

1. create a new virtualenv for lumigator
2. `cd notebooks` (assuming you were in the root directory of the repo)
3. `pip install -r requirements.txt`
4. `pip install jupyterlab` 
5. set up the environment so that both our backend and our ray cluster point to localhost and start jupyterlab:
```LUMIGATOR_SERVICE_HOST="localhost" RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR="localhost" jupyter-lab```

A new browser window will open pointing at your new jupyterlab. From there, open the `walkthrough.ipynb` file.

