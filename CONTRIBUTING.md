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

We manage contributions by having contributors file issues that are then worked against. You don't have to work on the issue you file. If you have found a bug or have a feature request, we want to know!

Below you'll find our contributing requirements and a step-by-step guide for developers to get up and running.
# Before We Begin...
If you need help with anything here, [Tech Support](https://www2.modzy.com/modzy-discord-chassis)  is graciously hosted on Modzy's discord server. The maintainers are active on that server and happy to assist contributors.
# Contributing Requirements

## Everbody

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
  2. Setup Docker Desktop
  3. Develop your code changes
  4. Document your changes
  5. Setup to debug Chassis
  6. Add test cases and comment them
- To contribute your changes:
  1. Add a descriptive commit message that clearly explain the Chassis code changes. 
  2. Create a descriptive pull request that references the original issue.

### Forking the Repo


#### 1. Clone the repository:

`$ git clone https://github.com/modzy/sdk-python.git`

#### 2. Setup a virtual environment from the local git directory:

| Environment | OS  | Command                                                                                            |
|-------------|-----|----------------------------------------------------------------------------------------------------|
| Conda       | Any | `$ conda create --name VIRTUAL_ENVIRON_NAME --file requirements_dev.txt -c conda-forge python=3.9` |
| Not Conda   | Any | `$ python3 -m venv /path/to/VIRTUAL_ENVIRON_NAME`                                                  |

#### 3. Activate the virtual environment:

| Environment | OS      | Command                                                 |
|-------------|---------|---------------------------------------------------------|
| Conda       | Any     | `$ conda activate VIRTUAL_ENVIRON_NAME`                 |
| Not Conda   | Linux   | `$ source /path/to/VIRTUAL_ENVIRON_NAME/bin/activate`   |
| Not Conda   | Windows | `C:>\path\to\VIRTUAL_ENVIRON_NAME\Scripts\activate.bat` |

#### 4. Install dependencies (if not using conda):

`$ pip3 install -r requirements_dev.txt`

#### 5. Create a branch for your awesome new feature:

`$ git checkout -b my-awesome-new-feature`

#### 6. A Special Note for Windows Users
Behind the scenes `git clone` silently does some line ending changes from LF to CRLF for you. Git also silently translates the line endings back to LF on `git commit` so usually this isn't an issue; however, Chassis builds Linux based containers and those line endings that went from LF to CRLF during `git clone` can cause problems for bash in Linux containers. To prevent this problem from occuring you need to use your IDE to set the line endings of  `chassis/service/flavours/mlflow/entrypoint.sh` to LF. You can google how to do this for your favorite IDE.

<br>

### Install Docker Desktop

Chassis has two (2) parts to it. 
1) An SDK that allows users to create a web request that will wrap their machine learning models along with peripheral information needed for testing the models.
2) An API accessible Service that processes a web request from the SDK into an [OMI](openmodel.ml) compliant container.

In deployment scenarios, the service runs on a Kubernetes cluster. This reality means that code contributions need to be tested against a Kubernetes cluster environment. To alleviate the need for contributors to have full access to a production Kubernetes cluster, Chassis's code has been factored to allow for a "Dev Mod" which is compatible with Docker Desktop's built in Kubernetes Cluster. 

#### To Setup for Chassis Development with Docker Desktop

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop): It is available across Windows, Mac, and Linux.
- Enable the built in Kubernetes Cluster from Docker Desktop's Setting. Example [here](https://birthday.play-with-docker.com/kubernetes-docker-desktop/)
- Set `CHASSIS_DEV=True` in your local repo's `chassis/service/app.py` file

<br>

### Develop your changes

Fix that bug or build your feature.

<br>

### Documentation

Chassis strives to maintain current, illuminating documentation. All contributions are expected to include documentation that allows fellow contributors to understand any code changes and the intent of the change. To have your contribution considered for inclusion it should have the follow associated with it: 

If you are adding or changing lines of code. make sure the intent is documented in the code through comments.

If you are adding a method to the code base you should document it using [Google's style guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#383-functions-and-methods) which requires providing an overview of the method, explainations for the arguements, an explaination for the return values, and any explainations for exceptions that can raise in the method. This approach will allow mkdocs to automatically generate our website documentation for Chassis.

Example: 
```python
    def fetch_smalltable_rows(table_handle: smalltable.Table,
                          keys: Sequence[Union[bytes, str]],
                          require_all_keys: bool = False,) -> Mapping[bytes, Tuple[str, ...]]:
    """Fetches rows from a Smalltable. 

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
        table_handle: An open smalltable.Table instance.
        keys: A sequence of strings representing the key of each table
          row to fetch.  String keys will be UTF-8 encoded.
        require_all_keys: If True only rows with values set for all keys will be
          returned.

    Returns:
        A dict mapping keys to the corresponding table row data
        fetched. Each row is represented as a tuple of strings. For
        example:

        {b'Serak': ('Rigel VII', 'Preparer'),
         b'Zim': ('Irk', 'Invader'),
         b'Lrrr': ('Omicron Persei 8', 'Emperor')}

        Returned keys are always bytes.  If a key from the keys argument is
        missing from the dictionary, then that row was not found in the
        table (and require_all_keys must have been False).

    Raises:
        IOError: An error occurred accessing the smalltable.
    """
```

  Also please check your spelling and grammar.

<br>

### Setting Up to Debug Chassis Locally
Chassis requires a few environment variables to run. most are prepackaged in the .env file; however, the local cluster config file needs to be set by the contributor.

- CHASSIS_KUBECONFIG - usually found at `~/.kube/config` or `C:\Users\<uname>\.kube\config`

To test Chassis code changes Chassis needs to run locally at some level. The way in which it needs to run depends on your update.
All test methods require helm so ...

1) install [helm](https://helm.sh/docs/intro/install/). The helm website covers Windows, Mac, and Linux

##### SDK Only Update

The Chassis API service can be installed through existing helm charts.

2) Add helm repo
   1) `helm repo add chassis https://modzy.github.io/chassis`
3) fetch Chassis charts
   1) `helm repo update`
4) install Chassis
   1) `helm install chassis chassis/chassis`
5) add ingress
   1) `kubectl expose deployment chassis --type=NodePort --port=5000 --name=chassis-ingress `
6) check ingress port
   1) `kubectl get service`
   produces a table showing you the local port that can be used to access Chassis
   
| NAME            | TYPE     | CLUSTER-IP | EXTERNAL-IP | PORT               | AGE |
|-----------------|----------|------------|-------------|--------------------|-----|
| chassis-ingress | NodePort | x.x.x.x    | none        | <5000> : localport | x   |

3) connect through browser 
   1) `http://localhost:localport`
   2) the browser should return with a message "Alive!"

SDK changes can now be tested against the `http://localhost:localport` endpoint.

##### Service Update


To run code in your IDE

2) set `CHASSIS_DEV=True` in chassis/service/app.py
3) start debug mode in your IDE
4) submit test cases against `localhost:5000` to hit your breakpoints in the IDE
   1) the notebook examples in the SDK examples make good test script bases


To run the "packaged" version of your changes 

6) set `CHASSIS_DEV=False` in `chassis/service/app.py`
7) build the service from inside the the `chassis/service` directory 
   1) `cd chassis/service`
   2) `docker build -t chassis-image:latest .`
8) install using the dev helm charts from inside the `chassis/chassis-dev-charts` directory
   1) `cd chassis/chassis-dev-charts`
   2) `helm install chassis .`
9) if there is no ingress, create one using step 5 from the SDK instructions
10) submit test chases against `localhost:localport`


<br>

### Update and Run Test Functionality
Before submitting a PR all contributor code should be tested to make sure that it

1) resolves the issue it is designed to resolve
2) doesn't break anything else

this requirement will become more strenuous with completion of [issue #60](https://github.com/modzy/chassis/issues/60) "Create Test Suite" at which point code changes will have to pass all related tests for PR approval.

<br>

## Contributing your code
We welcome your help in making Chassis better. In order to help insure the community can grow together, we ask that commits and PRs be meaningful. These are items that others will view in logs, and so specificity is a must for cooperative development.

<br>

### 1) Commit Format 
When commiting to a git branch an informative commit is requested. No format is required, but something like this is strongly recommended.
```
Updated [SDK | Service | Documentation | Other]:
Quick note on what was done

Commit Overview:
details on changes and their impacts for users as well as devs

Commit Known Issues:
details on issues not addressed by commit, but that need attention in the future.

Commit include:
list of files impacted.
```

<br>

### 2) PR Format
When filing a Pull Request, be descriptive as to what your PR addresses. Additionally use the keyword "resolves" so that Git will automatically link the PR to the issue it addresses.

Example:
```
This PR addresses the error message that you receive when you try to execute the SDK's xyz method by passing it an alphanumeric value.
resolves #42
```
<br>


# Where to go from here

If you are looking to get involved with Chassis please take a look at our [open issues](https://github.com/modzy/chassis/issues) and dive right in, or reach out to us on the [Discord server](https://www2.modzy.com/modzy-discord-chassis) with any questions on where to start.