class SerializeMixin:
    def __init__(self, *args, ignore_fields=None, set_hooks=None, **kwargs):
        self._ignore_fields = list() if ignore_fields is None else ignore_fields
        self._set_hooks = list() if set_hooks is None else set_hooks
        super().__init__(*args, **kwargs)

    def __getstate__(self):
        return {key: value for key, value in self.__dict__.items() if key not in self._ignore_fields}

    def __setstate__(self, state):
        self.__dict__ = state
        for hook in self._set_hooks:
            hook()
