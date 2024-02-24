from datetime import timedelta
import json
import os
import glob
from functools import partial
from typing import List, Tuple
from typing import Any
from typing import Dict
from typing import Optional

import boto3
from metadata import Metadata


def _path_creator(suffix: str, base_dir: str) -> str:
    return os.path.join(base_dir, suffix)


_metadata_dir = partial(_path_creator, "metadata")



SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_BASE_DIR = os.path.join(SCRIPT_DIR, "..", "config")

CONFIG_METADATA_DIR = _metadata_dir(CONFIG_BASE_DIR)



def _parse_json(file_path: str, throw_on_not_found: bool = True) -> Tuple[Any, str]:
    try:
        with open(file_path, "r") as fh:
            source_code = fh.read()
            return (json.loads(source_code), source_code)
    except json.decoder.JSONDecodeError as jde:
        if throw_on_not_found:
            raise ValueError(
                "Error while parsing {},".format(file_path), jde
            )
    except FileNotFoundError as fnfe:
        if throw_on_not_found:
            raise ValueError(
                "FileNotFound {},".format(file_path), fnfe
            )
    return {}, ""


def _get_optional_value(data: Any, name: str) -> Optional[str]:
    if isinstance(data, str):
        return None
    elif isinstance(data, dict):
        return data.get(name)
    else:
        raise ValueError("Unknown field value expression type, should be string or dict")





def load_metadata(
    metadata_base_dir: str = CONFIG_METADATA_DIR,
    env: Optional[str] = None,
    ci_version: Optional[str] = None,
) -> Metadata:
    if env is None:
        env = 'dev'

    env_data, _ = _parse_json(os.path.join(metadata_base_dir, "environment", "{}.json".format(env)), False)
    

    return Metadata(
        env_data=env_data if env_data else {},
        ci_version=ci_version,
    )



class LoaderContext():
    @staticmethod
    def get(
        base_dir: Optional[str] = None,
        metadata_base_dir: Optional[str] = None,
        env: Optional[str] = None,
        ci_version: Optional[str] = None,
    ) -> 'LoaderContext':
        if base_dir is None:
            base_dir = CONFIG_BASE_DIR
        if metadata_base_dir is None:
            metadata_base_dir = base_dir
        metadata = load_metadata(_metadata_dir(metadata_base_dir), env, ci_version)
        return LoaderContext(
            metadata=metadata,
            
        )

    def __init__(
        self,
        metadata: Metadata,
        
    ) -> None:
        self.metadata = metadata
       

    
