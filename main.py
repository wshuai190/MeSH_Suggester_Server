"""Convenience entry point — delegates to app.py."""
import runpy, os, sys

sys.argv[0] = os.path.join(os.path.dirname(__file__), "app.py")
runpy.run_path(sys.argv[0], run_name="__main__")
