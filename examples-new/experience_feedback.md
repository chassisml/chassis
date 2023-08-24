# Raw Feedback/thoughts/notes
- the `--editable` version isn't recognized by the python interpreter in vscode which is annoying
        - was able to fix by creating a `.vscode/settings.json` file

- error returned by model.test is unclear where it comes from
- NOTE TO SELF: using old method need to add legacy_predict_fn to ChassisModel instantiation

# Questions
- can we get rid of the proxy issue by hosting a base image in our modzy dockerhub account?
- block until complete functionality?
- recommended workflow for pulling container down?


# Bugs
- tf models still present cloudpickle issue (supported in 1.6?)
- when running lightgbm container (don't need for 1.5-beta --> add as issue when 1.5-beta is out the door):
```
  File "/app/chassis/server/omi/server.py", line 67, in Status
    modules = cloudpickle.load(f)
  File "/usr/local/lib/python3.9/site-packages/lightgbm/__init__.py", line 8, in <module>
    from .basic import Booster, Dataset, Sequence, register_logger
  File "/usr/local/lib/python3.9/site-packages/lightgbm/basic.py", line 221, in <module>
    _LIB = _load_lib()
  File "/usr/local/lib/python3.9/site-packages/lightgbm/basic.py", line 206, in _load_lib
    lib = ctypes.cdll.LoadLibrary(lib_path[0])
  File "/usr/local/lib/python3.9/ctypes/__init__.py", line 452, in LoadLibrary
    return self._dlltype(name)
  File "/usr/local/lib/python3.9/ctypes/__init__.py", line 374, in __init__
    self._handle = _dlopen(self._name, mode)
OSError: libgomp.so.1: cannot open shared object file: No such file or directory
```
see https://pypi.org/project/lightgbm/ for more details

- when trying to run a yolov5 model, got this error
```
  File "/app/chassis/server/omi/server.py", line 67, in Status
    modules = cloudpickle.load(f)
  File "/usr/local/lib/python3.9/site-packages/yolov5/__init__.py", line 1, in <module>
    from yolov5.helpers import YOLOv5
  File "/usr/local/lib/python3.9/site-packages/yolov5/helpers.py", line 4, in <module>
    from yolov5.models.common import AutoShape, DetectMultiBackend
  File "/usr/local/lib/python3.9/site-packages/yolov5/models/common.py", line 18, in <module>
    import cv2
  File "/usr/local/lib/python3.9/site-packages/cv2/__init__.py", line 181, in <module>
    bootstrap()
  File "/usr/local/lib/python3.9/site-packages/cv2/__init__.py", line 153, in bootstrap
    native_module = importlib.import_module("cv2")
  File "/usr/local/lib/python3.9/importlib/__init__.py", line 127, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

- still haven't figured out cpu version of torch


# Todo (examples)
- remove "publicly-hosted" svm sklearn example
- remove all ONNX models?
- remove PMML example that no longer works?


# docs specific todos
- ~~~look into versioning~~~
- overwrite docs
- alpha version
    - ~~~ home page --> tighten up a little ~~~ 
    - ~~~ bottom getting started --> change to local docker build ~~~
    - Fix margins on home page code block
    - ~~~ Getting started --> getting started (get rid of weirdness) ~~~
    - Getting started
        - ~~~ docker should be default method we point people towards ~~~
        - ~~~ remove chassis.app.modzy.com ~~~
        - ~~~ please install docker ~~~
            - ~~~ on a PC --> ~~~
            - ~~~ on a MAC --> ~~~
            - ~~~ on a Linux --> do this ~~~
        - ~~~ spin up resulting container locally and run an inference ~~~
    - ~~~ get rid of tutorials for alpha (except getting started) ~~~
    - how to guides (new approach local docker build)
        - pick five and document fully
        - hugging face
        - generative AI example
        - pytorch
        - tensorflow

        - remove common data types suport
        - ~~~ arm support remove for now ~~~
        - ~~~ gpu support for now ~~~
        - documenting model metadata
    - ~~~ reference --> docstrings ~~~
    - reference --> protofile ("Interfaces" --> OMI & KServe)
    - ~~~ get rid of conceptual guides for alpha ~~~
    - ~~~ kill FAQs and recreate as needed ~~~
    - ~~~ add 1.5 alpha tag ~~~


# Remaining todos
- figure out what to do with examples