class InfrastructureError(Exception):
    """Base exception for the infrastructure layer."""

    def __init__(self, message: str = "An infrastructure error occurred"):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class FileLoadingError(InfrastructureError):
    """Raised when file loading fails."""

    def __init__(self, path: str, message: str = "Failed to load file"):
        full_message = f"{message}: '{path}'"
        super().__init__(full_message)
        self.path = path


class InvalidPathError(InfrastructureError):
    """Raised when file path is invalid or unsafe."""

    def __init__(self, path: str, message: str = "Invalid or unsafe file path"):
        full_message = f"{message}: '{path}'"
        super().__init__(full_message)
        self.path = path


class DatasetNotFoundError(InfrastructureError):
    """Raised when no dataset can be loaded."""

    def __init__(
        self, dataset_name: str | None = None, message: str = "Dataset not found"
    ):
        if dataset_name:
            full_message = f"{message}: '{dataset_name}'"
        else:
            full_message = message
        super().__init__(full_message)
        self.dataset_name = dataset_name
