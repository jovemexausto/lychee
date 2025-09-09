# Esses tipos gão gerados automaticamente pelo Lychee
from shared_types.customer import Customer


def main():
    import os

    # Exemplo de envs globais e por serviço
    print("Olá 👋, essa são suas [red]configurações[/] de ambiente personalizadas:")
    print(
        f"lychee.yaml -> {os.environ.get('MY_GLOBAL_ENV', 'oh, não, algo esstá errado.')}"
    )
    print(
        f"services/bar/service.yaml -> {os.environ.get('MY_LOCAL_ENV', 'oh, não, algo esstá errado.')}"
    )


if __name__ == "__main__":
    main()
