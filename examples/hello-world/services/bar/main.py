# Esses tipos gão gerados automaticamente pelo Lychee
from types.customer import Customer


def main():
    import os
    from logging import getLogger

    logger = getLogger(__name__)
    # Exemplo de envs globais e por serviço
    logger.info("Olá 👋, essa são suas configurações de ambiente personalizadas:")
    logger.info(f"lychee.yaml -> {os.environ.get('MY_GLOBAL_ENV', 'oh, não, algo esstá errado.')}")
    logger.info(f".../services/bar/service.yaml -> {os.environ.get('MY_LOCAL_ENV', 'oh, não, algo esstá errado.')}")


if __name__ == "__main__":
    main()
