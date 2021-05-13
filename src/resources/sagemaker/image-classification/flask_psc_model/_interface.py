from abc import ABC, abstractmethod


class ModelBase(ABC):
    """Model classes should extend this base class."""

    @abstractmethod
    def run(self, *filepaths):
        """Run the model on the given input file paths and write to the given output file paths.

        The input files paths followed by the output file paths will be passed into this function as
        positional arguments in the same order as specified in `input_filenames` and `output_filenames`.

        For example:
        ```
        class SingleInputOutputModel(ModelBase):
            input_filenames = ['input.txt']
            output_filenames = ['output.json']

            def run(self, input, output):
                run_the_model(input, output)

        class MultipleInputOutputModel(ModelBase):
            input_filenames = ['input1.png', 'input2.json', 'input3.txt']
            output_filenames = ['output1.png', 'output2.json']

            def run(self, input1, input2, input3, output1, output2):
                run_the_model(input1, input2, input3, output1, output2)
        ```
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def input_filenames(self):
        """A single string filename or a list of string filenames that the model expects as inputs.

        For example, both of the following are valid:
        ```
        class SingleInputModel(ModelBase):
            input_filenames = 'input.txt'
            ...

        class MultiInputModel(ModelBase):
            input_filenames = ['input.txt', 'config.json']
            ...
        ```
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def output_filenames(self):
        """A single string filename or a list of string filenames that the model will write as outputs.

        For example, both of the following are valid:
        ```
        class SingleOuputModel(ModelBase):
            output_filenames = 'output.txt'
            ...

        class MultiOutputModel(ModelBase):
            output_filenames = ['output.txt', 'metadata.json']
            ...
        ```
        """
        raise NotImplementedError

    @property
    def validation_exception_class(self):
        """The `Exception` subclass the `run()` function will raise to indicate a validation error of
        the input data. The string representation of the exception will be used as the error message.
        """
        return ValueError

    @property
    def io_exception_class(self):
        """The `Exception` subclass the `run()` function will raise to indicate an issue reading from
        the input or output file paths. The `filename` attribute of the exception must indicate which
        file the model was unable to read or write to (this is the default for the exceptions raised
        by the standard library `open` function).
        """
        return IOError

    @classmethod
    def __subclasshook__(cls, C):
        if cls is not ModelBase:
            return NotImplemented
        attrs = ['run', 'input_filenames', 'output_filenames', 'validation_exception_class', 'io_exception_class']
        for attr in attrs:
            for B in C.__mro__:
                if attr in B.__dict__:
                    if B.__dict__[attr] is None:
                        return NotImplemented
                    break
            else:
                return NotImplemented
        return True
