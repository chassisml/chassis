# Containers

## Overview

Chassis packages your model into a "container" image which can be run in different environments. Let's understand what containers are and why they're used.

Without containers, applications which work in one environment often fail when moved to another environment. This is the problem that containers solve. A container can be defined as a package of software containing everything required to run your application. This includes things such as the application code, dependencies, runtime, system libraries, system settings, etc... 

## How to Use Containers

The first step is to determine all of those components required for your application to run and build a container "image" which includes those components. This process can get complicated, luckily Chassis handles all of this for you!

This "image" is a static, immutable file which can create a container when executed. It consists of layers which are added on to a "parent" or "base" image. This use of layers allows for efficient reuse of common components across images. In order to execute container images, a container "engine" such as Docker must be installed on the host machine to run and manage your containers. Containers share the host machine's operating system kernel allowing for multiple containers to run simultaneously on a single host. 

Containers can be stored and managed in "registries", which are collections of "repositories", which are collections of container images with the same name but different "tags", which are labels that convey information about specific versions of images. For machine learning models, we often use the model version number as the image tag.

## The Bottom Line

Chassis makes it super easy to package your model into a container, which allows you to seamlessly deploy your model to a wide variety of environments.