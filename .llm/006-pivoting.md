Você acertou no ponto crucial: o projeto Lychee está tentando ser ambicioso demais e corre o risco de se tornar uma ferramenta genérica. A sua analogia com o `astral.sh` é perfeita. Ferramentas focadas, como `ruff` e `uv`, são muito mais poderosas do que uma única ferramenta que tenta fazer tudo.

Vamos reestruturar o projeto Lychee para seguir essa filosofia. A ideia é ter **uma suíte de ferramentas Lychee**, cada uma com um propósito claro e específico, mas que trabalham em perfeita harmonia sob a mesma marca.

---

## 🍊 A Suíte de Ferramentas Lychee

Em vez de um único projeto `lychee`, propomos dois componentes centrais e distintos, cada um com sua própria responsabilidade e um `README` focado. O CLI principal (`lx`) atuará como o orquestrador que chama as ferramentas apropriadas.

### 1. Lychee Contracts (Biblioteca)

Esta será a ferramenta fundamental para o desenvolvimento "schema-first". Seu foco é único: **gerar código tipado a partir de um schema de fonte única da verdade.** Ela resolve o "problema do inferno de integração" e a "troca de contexto de tipo".

**Funcionalidades Principais:**

- **Geração de Tipos**: Compilação de JSON Schema para modelos nativos de linguagens como Pydantic (Python) e Zod/TypeScript.
- **Gerenciamento de Symlinks**: Lida com a criação e atualização de symlinks para compartilhar os tipos gerados entre serviços.
- **Observador de Arquivos**: Monitora alterações em arquivos de schema (`.schema.json`) e dispara a regeneração automática.
- **API Programática**: Fornece uma API para que outras ferramentas (como o `Lychee Compose`) possam integrá-la.

**Comandos CLI (`lx contracts`):**

- `lx contracts generate`: Gera tipos a partir de um schema específico.
- `lx contracts watch`: Inicia um observador de arquivos que regenera os tipos automaticamente.

### 2. Lychee Compose (CLI)

Esta será a ferramenta de orquestração do monorepo. Seu foco é **simplificar o ambiente de desenvolvimento local, a partir de uma única fonte de verdade (`service.yml`)**. Ela resolve a "sobrecarga cognitiva" e o "feedback lento".

**Funcionalidades Principais:**

- **Orquestração de Serviços**: Lê o `service.yml` para entender a hierarquia de dependências e inicia os serviços na ordem correta.
- **Dashboard Unificado**: Apresenta a interface TUI com logs agregados, status de serviço e mensagens de erro.
- **Hot Reloading Inteligente**: Inicia observadores de arquivos para reiniciar serviços específicos quando o código-fonte muda.
- **Gerenciamento de Ambiente**: Garante o uso da versão correta da linguagem (por exemplo, `python 3.11.4`) para cada serviço.
- **Proxy Simples**: Inclui um proxy reverso in-process para rotear o tráfego local.

**Comandos CLI (`lx dev`):**

- `lx dev start`: O comando principal para iniciar todos os serviços.
- `lx dev restart <service_name>`: Reinicia um serviço específico.
- `lx dev logs <service_name>`: Mostra os logs de um único serviço.

---

## 🗺️ Novo Plano de Ação

Com a arquitetura clara em mente, podemos reformular o roadmap parag priorizar a construção dos componentes de forma modular.

### ⏳ Fase 1: Construindo as Fundações (Lychee Contracts MVP)

- **Definição do `service.yml`**: Criar o modelo do `service.yml` como a fonte de verdade para a orquestração.
- **Geração de Tipos**: Focar no core: gerar modelos **Pydantic** a partir de JSON Schema.
- **Gerenciamento de Symlinks**: Implementar a lógica para criar e gerenciar symlinks de forma segura.
- **Watcher de Schemas**: Criar o sistema de observação de arquivos que integra o **Lychee Contracts** de forma reativa.

### ⌛ Fase 2: O Núcleo do DX (Lychee Compose MVP)

- **Orquestrador Básico**: Implementar a lógica para ler o `service.yml`, iniciar serviços em ordem de dependência e gerenciar seus processos.
- **Dashboard TUI**: Construir a interface `Rich` para mostrar o status de serviço e logs.
- **Orquestração de Linguagem**: Adicionar a lógica para usar a versão correta do Python com base no `service.yml`.
- **Integração com Lychee Contracts**: Fazer com que o **Lychee Compose** use a biblioteca **Lychee Contracts** para monitorar e regenerar schemas quando necessário.

---

Esta abordagem resolve a ambiguidade e cria dois projetos distintos, mas complementares. O **Lychee Contracts** é a "engrenagem" que garante a segurança de tipos, enquanto o **Lychee Compose** é a "caixa de ferramentas" que simplifica o fluxo de trabalho. Juntos, eles formam a suíte **Lychee** que você visualizou.
