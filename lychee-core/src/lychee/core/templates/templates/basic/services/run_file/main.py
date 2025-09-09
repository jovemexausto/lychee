def main():
    import os

    print("Hi 👋, this is your custom env settings:")
    print(f"lychee.yaml: {os.environ.get('MY_GLOBAL_ENV', 'oh no, something is broken')}")
    print(
        f"run_file/service.yaml: {os.environ.get('MY_LOCAL_ENV', 'oh no, something is broken')}"
    )
