"""Resolve an explicitly recorded private Windows worker workspace.

Missing worker_root retains the original C workspace. D is selected only by
the specification; a command-line override must agree with that record.
"""
import json
from pathlib import Path, PureWindowsPath

DEFAULT_WORKER_ROOT = PureWindowsPath('C:/Projects/TimeLearnerWorker')
ALLOWED_WORKER_ROOTS = (DEFAULT_WORKER_ROOT, PureWindowsPath('D:/Projects/TimeLearnerWorker'))


def declared_worker_root(specification, requested=None):
    value = specification.get('worker_root', str(DEFAULT_WORKER_ROOT))
    if type(value) is not str:
        raise RuntimeError('invalid_declared_worker_root')
    root = PureWindowsPath(value)
    if not root.is_absolute() or '..' in root.parts or root not in ALLOWED_WORKER_ROOTS:
        raise RuntimeError('unsupported_private_worker_root')
    if requested is not None and PureWindowsPath(str(requested)) != root:
        raise RuntimeError('worker_root_override_differs_from_specification')
    return root


def load_specification(value, requested=None):
    path = Path(value).absolute()
    if not any(path != Path(str(root)) and path.is_relative_to(Path(str(root)))
               for root in ALLOWED_WORKER_ROOTS):
        raise RuntimeError('specification_outside_private_worker_workspaces')
    if any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)):
        raise RuntimeError('reparse_specification_path')
    specification = json.loads(path.read_bytes())
    if type(specification) is not dict:
        raise RuntimeError('invalid_worker_specification')
    root = Path(str(declared_worker_root(specification, requested)))
    if path == root or not path.is_relative_to(root):
        raise RuntimeError('specification_outside_declared_worker_root')
    if not root.is_dir() or any(p.is_symlink() or p.is_junction() for p in (root, *root.parents)):
        raise RuntimeError('invalid_physical_worker_root')
    return path.resolve(strict=True), specification, root.resolve(strict=True)
