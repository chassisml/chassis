![Chassis logo](https://github.com/modzy/chassis/blob/main/docs/docs/images/chassis-logo.png)

# Chassis Example Notebooks

## Goals

In these notebooks, we'll show you how easy it is to use Chassis and the Chassis SDK to containerize and deploy different types of models built using different tools.

**Setup**

- First, you'll need a running instance of the Chassis service
    - Follow instructions [here](https://chassis.ml/tutorials/devops-deploy/) to get Chassis up and running
- Install [Anaconda](https://www.anaconda.com/products/individual)
- Install Jupyter: `conda install -c anaconda jupyter`
- Clone this repo: `git clone https://github.com/modzy/chassis`
- Get to this subdirectory: `cd chassis/chassisml-sdk/examples`
- Create demo conda environment from file: `conda env create -f conda.yaml`
- Activate environment (you may need to use a new terminal): `conda activate chassis-demo`
- Make environment accessible to Jupyter: `python -m ipykernel install --user --name=chassis-demo`
- Open Jupyter notebook: `jupyter notebook`
- Open one of the notebooks in this subdirectory
- Make sure to activate the correct environment
    - In the notebook, `Kernel`->`Change Kernel`->`chassis-demo`
- Start running the notebook, more info and instructions are provided there!

## Contributors

A full list of contributors, which includes individuals that have contributed entries, can be found [here](https://github.com/modzy/chassis/graphs/contributors).