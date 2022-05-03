import mxnet as mx
import onnxruntime as ort
ort.set_default_logger_severity(3)

class WrappedInferenceSession:

    def __init__(self, onnx_bytes):
        self.sess = ort.InferenceSession(onnx_bytes)
        self.onnx_bytes = onnx_bytes

    def run(self, *args):
        return self.sess.run(*args)

    def __getstate__(self):
        return {'onnx_bytes': self.onnx_bytes}

    def __setstate__(self, values):
        self.onnx_bytes = values['onnx_bytes']
        self.sess = ort.InferenceSession(self.onnx_bytes)  
    