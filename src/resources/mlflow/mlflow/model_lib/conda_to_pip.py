import pathlib
import os

ROOT_DIR = pathlib.Path(__file__).parent
CONDA_YAML = ROOT_DIR / "weights" / "conda.yaml"


def conda_to_pip():
    deps = []
    seen_deps = False
    seen_pip = False
    with open(CONDA_YAML, 'r') as f:
        for line in f:
            line = line.strip()
            # print(line)
            if line == "dependencies:":
                seen_deps = True
                continue

            if line == "- pip:":
                seen_deps = False
                seen_pip = True
                continue

            if line == "name: mlflow-env":
                seen_pip = False
                continue

            if seen_deps or seen_pip:
                dep = line.strip("- ")
                if "python" in dep or dep == "pip":
                    continue
                else:
                    if seen_deps and not seen_pip:
                        dep = dep.replace("=", "==")
                        dep = dep.replace("pytorch", "torch")
                    deps.append(dep)

    outfile_path = ROOT_DIR.parent / "mlflow_reqs.txt"
    #print(f"writing to {outfile_path}")
    #print(f"{os.listdir('/opt/app/model_lib/') = }")
    #print(f"{os.listdir('/opt/app/model_lib/weights') = }")
    with open(outfile_path, "w") as f:
        for d in deps:
            f.write(d + "\n")


if __name__ == '__main__':
    conda_to_pip()
