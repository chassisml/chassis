<div align="center">

<!-- ![chassis-banner-v1.3.png](https://raw.githubusercontent.com/modzy/chassis/main/chassis-banner-v1.3.png) -->
![chassis-banner-v1.3.png](https://raw.githubusercontent.com/modzy/chassis/main/chassis-banner-v1.3.png)

![GitHub contributors](https://img.shields.io/github/contributors/modzy/chassis?logo=GitHub&style=flat)
![GitHub last commit](https://img.shields.io/github/last-commit/modzy/chassis?logo=GitHub&style=flat)
![GitHub issues](https://img.shields.io/github/issues-raw/modzy/chassis?logo=github&style=flat)
![GitHub](https://img.shields.io/github/license/modzy/chassis?logo=apache&style=flat)

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/modzy/chassis/ci.yml?logo=github)
![PyPI](https://img.shields.io/pypi/v/chassisml?logo=pypi&style=flat)
![PyPI - Downloads](https://img.shields.io/pypi/dm/chassisml?logo=pypi&style=flat)

<h3 align="center">
  <a href="https://chassisml.io">Docs</a>
  <span> · </span>
  <a href="https://discord.gg/anSeEj8ARg">Discord</a> (#chassisml)
  <span> · </span>
  <a href="https://go.mlops.community/slack">Slack</a> (#chassis-model-builder)ha
  
</h3>

</div>

# What is Chassis?
<div align="center">

<!-- <img src="https://raw.githubusercontent.com/modzy/chassis/main/docs/docs/images/what-is-chassis.png" alt="what-is-chassis-diagram" width="650"/> -->

<img src="https://raw.githubusercontent.com/modzy/chassis/main/docs/docs/images/what-is-chassis.png" alt="what-is-chassis-diagram" width="600"/>

<br>

</div>

Chassis turns ML models written in Python into containerized prediction APIs in just minutes. We built it to be an easier way to put our models into containers and ship them to production.

Chassis picks up right where your training code leaves off and builds containers for a variety of target architectures. This means that after completing a single Chassis job, you can run your models in the cloud, on-prem, or on a fleet of edge devices (Raspberry Pi, NVIDIA Jetson Nano, Intel NUC, etc.).

## Benefits
* <img height="16" width="16" src="https://cdn.simpleicons.org/docker/0092DF" /> Turns models into containers, automatically
* <img height="16" width="16" src="https://cdn.simpleicons.org/linuxfoundation/0092DF" /> Creates easy-to-use prediction APIs
* <img height="16" width="16" src="https://cdn.simpleicons.org/kubernetes/0092DF" /> Builds containers locally on Docker or as a K8s service
* <img height="16" width="16" src="https://cdn.simpleicons.org/docker/0092DF" /> Chassis containers run on Docker, containerd, Modzy, and more
* <img height="16" width="16" src="https://cdn.simpleicons.org/intel/0092DF" /> Compiles for both x86 and ARM processors
* <img height="16" width="16" src="https://cdn.simpleicons.org/nvidia/0092DF" /> Supports GPU batch processing
* <img height="16" width="16" src="https://cdn.simpleicons.org/pypi/0092DF" /> No missing dependencies, perfect for edge AI

# Installation
Install Chassis on your machine or in a virtual environment via [PyPi](https://pypi.org/project/chassisml/):

### Stable - v1.5.*
```bash
pip install "chassisml[quickstart]"
```

# Try it out

### [Quickstart Guide](https://chassisml.io/v1.5/getting-started/quickstart/)
(<5 minutes)

### [Full Workflow](https://chassisml.io/v1.5/getting-started/full-workflow/)
(~10 minutes)

# Docs

📗 [Getting Started](https://chassisml.io/v1.5/getting-started/)

📘 [Full Docs](https://chassisml.io)

Framework-specific examples:
<table>
    <tr>
        <td>🤗 <a href="https://chassisml.io/v1.5/guides/frameworks/diffusers/">Diffusers</a></td>
        <td> <!-- JSDelivr --> <img height="16" width="16" src="https://cdn.simpleicons.org/pytorch" /> <a href="https://chassisml.io/v1.5/guides/frameworks/torch/">Torch</a></td>
        <td>🤗 <a href="https://chassisml.io/v1.5/guides/frameworks/transformers/">Transformers</a></td>
        <td>Coming soon...</td>
    </tr>
</table>

# Support

Join the `#chassisml` channel on [Modzy's Discord Server](https://discord.gg/eW4kHSm3Z5) where our maintainers meet to plan changes and improvements.

We also have a `#chassis-model-builder` Slack channel on the [MLOps.community Slack](https://go.mlops.community/slack)!


## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/bmunday3"><img src="https://avatars.githubusercontent.com/u/99284020?v=4?s=100" width="100px;" alt="Bradley Munday"/><br /><sub><b>Bradley Munday</b></sub></a><br /><a href="https://github.com/modzy/chassis/commits?author=bmunday3" title="Code">💻</a> <a href="#ideas-bmunday3" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-bmunday3" title="Maintenance">🚧</a> <a href="#question-bmunday3" title="Answering Questions">💬</a></td>
      <td align="center"><a href="https://github.com/caradoxical"><img src="https://avatars.githubusercontent.com/u/1461827?v=4?s=100" width="100px;" alt="Seth Clark"/><br /><sub><b>Seth Clark</b></sub></a><br /><a href="#content-caradoxical" title="Content">🖋</a> <a href="https://github.com/modzy/chassis/commits?author=caradoxical" title="Documentation">📖</a> <a href="#projectManagement-caradoxical" title="Project Management">📆</a></td>
      <td align="center"><a href="https://github.com/DataScienceDeconstructed"><img src="https://avatars.githubusercontent.com/u/34408482?v=4?s=100" width="100px;" alt="Clayton Davis"/><br /><sub><b>Clayton Davis</b></sub></a><br /><a href="https://github.com/modzy/chassis/commits?author=DataScienceDeconstructed" title="Code">💻</a> <a href="https://github.com/modzy/chassis/commits?author=DataScienceDeconstructed" title="Documentation">📖</a> <a href="#ideas-DataScienceDeconstructed" title="Ideas, Planning, & Feedback">🤔</a> <a href="#projectManagement-DataScienceDeconstructed" title="Project Management">📆</a></td>
      <td align="center"><a href="http://n8mellis.net"><img src="https://avatars.githubusercontent.com/u/39227?v=4?s=100" width="100px;" alt="Nathan Mellis"/><br /><sub><b>Nathan Mellis</b></sub></a><br /><a href="#ideas-n8mellis" title="Ideas, Planning, & Feedback">🤔</a> <a href="#infra-n8mellis" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/modzy/chassis/commits?author=n8mellis" title="Code">💻</a></td>
      <td align="center"><a href="https://github.com/saumil-d"><img src="https://avatars.githubusercontent.com/u/83971510?v=4?s=100" width="100px;" alt="saumil-d"/><br /><sub><b>saumil-d</b></sub></a><br /><a href="https://github.com/modzy/chassis/commits?author=saumil-d" title="Code">💻</a> <a href="https://github.com/modzy/chassis/commits?author=saumil-d" title="Documentation">📖</a> <a href="#tutorial-saumil-d" title="Tutorials">✅</a> <a href="#ideas-saumil-d" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
    <tr>
      <td align="center"><a href="https://github.com/lukemarsden"><img src="https://avatars.githubusercontent.com/u/264658?v=4?s=100" width="100px;" alt="lukemarsden"/><br /><sub><b>lukemarsden</b></sub></a><br /><a href="https://github.com/modzy/chassis/commits?author=lukemarsden" title="Documentation">📖</a> <a href="#projectManagement-lukemarsden" title="Project Management">📆</a> <a href="#ideas-lukemarsden" title="Ideas, Planning, & Feedback">🤔</a> <a href="#talk-lukemarsden" title="Talks">📢</a> <a href="#video-lukemarsden" title="Videos">📹</a></td>
      <td align="center"><a href="https://carmilso.com"><img src="https://avatars.githubusercontent.com/u/7313231?v=4?s=100" width="100px;" alt="Carlos Millán Soler"/><br /><sub><b>Carlos Millán Soler</b></sub></a><br /><a href="https://github.com/modzy/chassis/commits?author=carmilso" title="Code">💻</a></td>
      <td align="center"><a href="https://www.linkedin.com/in/douglas-holman/"><img src="https://avatars.githubusercontent.com/u/35512326?v=4?s=100" width="100px;" alt="Douglas Holman"/><br /><sub><b>Douglas Holman</b></sub></a><br /><a href="https://github.com/modzy/chassis/commits?author=DHolmanCoding" title="Code">💻</a></td>
      <td align="center"><a href="https://github.com/philwinder"><img src="https://avatars.githubusercontent.com/u/8793723?v=4?s=100" width="100px;" alt="Phil Winder"/><br /><sub><b>Phil Winder</b></sub></a><br /><a href="#ideas-philwinder" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center"><a href="https://github.com/sonejah21"><img src="https://avatars.githubusercontent.com/u/5269893?v=4?s=100" width="100px;" alt="Sonja Hall"/><br /><sub><b>Sonja Hall</b></sub></a><br /><a href="#design-sonejah21" title="Design">🎨</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
