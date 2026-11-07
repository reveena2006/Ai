from pathlib import Path

path = Path("app.py")
code = path.read_text(encoding="utf-8")

# 1. Add get_pipeline_python function after PIPELINE_SCRIPT
target_pipeline_script = 'PIPELINE_SCRIPT = BASE_DIR / "run_both_rankers.py"'
helper_code = '''PIPELINE_SCRIPT = BASE_DIR / "run_both_rankers.py"


def get_pipeline_python():
    """Return the Python interpreter that has the full ML dependencies installed."""
    try:
        import sentence_transformers  # noqa: F401
        return sys.executable
    except ImportError:
        venv312_py = BASE_DIR / ".venv312" / "Scripts" / "python.exe"
        if venv312_py.exists():
            return str(venv312_py)
        return sys.executable'''

if target_pipeline_script in code:
    code = code.replace(target_pipeline_script, helper_code, 1)
    print("Added get_pipeline_python helper.")
else:
    print("Error: PIPELINE_SCRIPT target not found.")

# 2. Update subprocess.run call
target_subprocess = '[sys.executable, str(PIPELINE_SCRIPT)],'
replacement_subprocess = '[get_pipeline_python(), str(PIPELINE_SCRIPT)],'

if target_subprocess in code:
    code = code.replace(target_subprocess, replacement_subprocess, 1)
    print("Updated subprocess.run to use get_pipeline_python().")
else:
    print("Error: target_subprocess not found.")

path.write_text(code, encoding="utf-8")
print("SUCCESS: app.py updated.")
