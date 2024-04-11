from typing import Dict, List
from typing import Any
from typing import Tuple
from typing import Optional


class Metadata():
    def __init__(
        self,        
        env_data: Dict[str, Any]
    ) -> None:       
        self._env_data = env_data       

    def get_env(self, *path: str) -> str:
        return self._get_val("env", path, self._env_data, None)

    def get_env_values(self, *path: str) -> List[str]:
        val = self._get_val("env", path, self._env_data, None)
        assert isinstance(val, dict)
        return list(val.values())

    def get_env_default(self, default, *path: str) -> str:
        return self._get_val("env", path, self._env_data, default)   

    def _get_val(self, label: str, path: Tuple[str, ...], data: Dict[str, Any], default: Optional[str]) -> Any:
        assert len(path) > 0
        current_data = data
        for key in path[:-1]:
            if key not in current_data and default is None:
                raise ValueError("Key '{}' for path '{}' not found in {} metadata".format(key, label, ".".join(path)))
            current_data = current_data[key]
            assert isinstance(current_data, dict)

        if default is None:
            return current_data[path[-1]]
        else:
            return current_data.get(path[-1], default)