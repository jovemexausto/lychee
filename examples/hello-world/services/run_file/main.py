def main():
    import os
    from logging import getLogger

    logger = getLogger(__name__)

    logger.info("Hi 👋, this is your custom env settings:")
    logger.info(f"lychee.yaml: {os.environ.get('MY_GLOBAL_ENV', 'oh no, something is broken')}")
    logger.info(f"run_file/service.yaml: {os.environ.get('MY_LOCAL_ENV', 'oh no, something is broken')}")


if __name__ == "__main__":
    main()
