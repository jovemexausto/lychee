# 🚀 Template Básico de Projeto

Este template oferece uma estrutura **monorepo** mínima com dois serviços simples para você começar com o pé direito.

## 📦 Inclui

- `lychee.yml`: O arquivo principal de configuração do **Lychee**.
- `services/foo`: Um serviço de exemplo em **Python** utilizando **FastAPI**.
- `services/bar`: Um serviço de exemplo em **Python** executando um script de arquivo.

## 🔍 Explore mais

Cada serviço possui seu próprio arquivo `service.yml`, que define suas configurações específicas. Vale a pena explorá-lo para entender como os serviços se integram ao Lychee e como você pode personalizá-los conforme suas necessidades.

Além disso, os **schemas** definidos globalmente são convertidos automaticamente para modelos **Pydantic** e incluídos em cada serviço por meio de **symlinks**. Isso garante consistência entre os serviços e facilita a validação de dados sem duplicação de código.
