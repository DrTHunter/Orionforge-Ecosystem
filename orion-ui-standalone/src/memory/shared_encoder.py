"""One copy of each sentence-embedding model per process.

Every FAISS memory (the owner's and each signed-in user's), the notes index and
the AGI loop's field used to load their own copy of the same model: seconds of
load time and ~100 MB of memory each. They now share one per model name.

The Hugging Face fast tokenizer can raise "Already borrowed" when two threads
encode at once, so a shared model encodes one call at a time (each is a few ms).
"""

import threading
from typing import Any, Callable, Dict, Tuple

_models: Dict[Tuple[str, Any], "_SharedModel"] = {}
_lock = threading.Lock()


class _SharedModel:
    """The model, with ``encode`` serialized; everything else passes through."""

    def __init__(self, model):
        self._model = model
        self._encode_lock = threading.Lock()

    def encode(self, *args, **kwargs):
        with self._encode_lock:
            return self._model.encode(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._model, name)


def shared_encoder(model_name: str, factory: Callable[[str], Any]):
    """The process-wide model for ``model_name``, built with ``factory`` on first use."""
    key = (model_name, factory)
    model = _models.get(key)
    if model is None:
        with _lock:
            model = _models.get(key)
            if model is None:
                model = _models[key] = _SharedModel(factory(model_name))
    return model
