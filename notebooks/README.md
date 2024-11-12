# Lumigator Demo Notebooks

A collection of Jupyter notebooks and scripts showcasing Lumigator's functionalities. For installing
Lumigator, see the main [README.md](README.md)

The notebook runs on Jupyter. If you don't yet have Jupyter set up:

1. Create a new virtualenv for lumigator by running `python3 -m venv lumigator`, or, if
   you're using `uv`, `uv venv lumigator`.
1. Activate the virtualenv: `source lumigator/bin/activate`.
1. Navigate into the Notebooks directory: `cd notebooks` (assuming you were in the root directory of
   the repo).
1. Install the necessary requirements: `pip install -r requirements.txt`.
1. Set up the environment so that both our backend and our Ray cluster point to localhost and start
   `jupyterlab`:

    ```
    LUMIGATOR_SERVICE_HOST="localhost" \
    RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR="localhost" \
    jupyter-lab
    ```

    > Note: Set any other environment variables you need to configure the backend or Ray cluster,
    > such as `MISTRAL_API_KEY` and `OPENAI_API_KEY`.

A new browser window will open pointing at your new jupyterlab. From there, open the
`walkthrough.ipynb` file.
