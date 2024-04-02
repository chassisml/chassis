import cloudpickle


def load(pkl_path):
    with open(pkl_path, "rb") as p:
        return cloudpickle.load(p)
