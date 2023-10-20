#!/usr/bin/env python3

import os

"""
A list of pip requirements that are modified when writing out the container's
`requirements.txt`.

Items in this list are primarily to ensure that large packages that have a
headless variant use the headless variant since the container doesn't use a
display.
"""
REQUIREMENTS_SUBSTITUTIONS = {
    "opencv-python=": "opencv-python-headless="
}

requirements_txt = "requirements.txt"

# Post-process the full requirements.txt with automatic replacements.
with open(requirements_txt, "rb") as f:
    reqs = f.read().decode()
for old, new in REQUIREMENTS_SUBSTITUTIONS.items():
    reqs = reqs.replace(old, new)
if "torch" in reqs and not os.getenv("GPU").strip() == "true":
    reqs = "--extra-index-url https://download.pytorch.org/whl/cpu\n\n" + reqs
with open(requirements_txt, "wb") as f:
    f.write(reqs.encode())
