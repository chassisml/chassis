<div align="center">

<h1>Contributing to Chassis</h1>

<br>
<br>
<br>
<br>



<img alt="GitHub contributors" src="https://img.shields.io/github/contributors/modzy/chassis">

<img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/modzy/chassis">

<img alt="GitHub Release Date" src="https://img.shields.io/github/issues-raw/modzy/chassis">

<br>
<br>

<a href="/CODE_OF_CONDUCT.md" style="text-decoration:none">
    <img src="https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg" alt="Contributor Covenant" style="max-width:100%;">
</a>


</div>
<br>
<br>

<div align="center">
<a href="/README.md" style="text-decoration:none">Readme</a> |
<a href="https://chassis.ml" style="text-decoration:none">Documentation</a>

</div>

<br>
<br>
<br>
<br>



Contributions are welcome and they are greatly appreciated! Every little bit helps, and credit will always be given.

We manage contributions by having contributors file issues that are then worked against. You don't have to work on the issues to  file it. If you have found a bug or have a feature request, we want to know!

Below you'll find our contributing requirements, a step-by-step guideline, and our features roadmap.

#Contributing Requirements

##Everbody
- Search previous [issues](https://github.com/modzy/chassis/issues) before making new ones to avoid duplicates.
- If you are reporting a new bug, create an issue including:
  1. Your operating system name and version.
  2. Any details about your local setup that might be helpful in troubleshooting.
  3. Detailed steps to reproduce the bug.
- If you are proposing a new feature, create an issue including:
  1. Explain in detail how it would work.
  2. Keep the scope as narrow as possible, to make it easier to implement.
  3. Remember that this is a volunteer-driven project, and that contributions are welcome.
- File your issue to let us know it's important to you.

## If you are going to develop for Chassis
- To develop for Chassis:
  1. Fork the repo 
  2. Develop **and test** your code changes
  3. Use descriptive comments throughout your code.
  4. Add supporting documentation.
  5. Check your spelling and grammar.
  6. Add test cases and comment them.
- To contribute your changes:
  1. Add a descriptive commit message that clearly explain the Chassis code changes. 
  2. Create a descriptive pull request that references the original issue.


###Guidelines

 1. Fork the repo and set it for local development

Clone the repository:

- `$ git clone https://github.com/modzy/sdk-python.git`

Setup a virtual environment from the local git directory:

- `$ conda create --name VIRTUAL_ENVIRON_NAME --file requirements_dev.txt -c conda-forge python=3.9`

or for non-conda python distros:
- `$ python3 -m venv /path/to/VIRTUAL_ENVIRON_NAME`

Activate the virtual environment:

- `$ conda activate VIRTUAL_ENVIRON_NAME`

or for non-conda python distros: 

On Linux use source to activate

- `$ source /path/to/VIRTUAL_ENVIRON_NAME/bin/activate`

On Windows run the activate.bat file

- `C:>\path\to\VIRTUAL_ENVIRON_NAME\Scripts\activate.bat`


Install dependencies (if not using conda):

- `$ pip3 install -r requirements_dev.txt`


Create a branch for your awesome new feature:

- `$ git checkout -b my-awesome-new-feature`

<br>

### Develop your changes

Fix that bug or build your feature.

