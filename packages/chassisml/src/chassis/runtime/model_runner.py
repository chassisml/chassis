class ModelRunner:

    def __init__(self, predict_fn, supports_batch: bool = False, batch_size: int = 1):
        self.predict_fn = predict_fn
        self.supports_batch = supports_batch
        self.batch_size = batch_size

    def predict(self, inputs):
        return self.predict_fn(inputs)
