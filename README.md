<br />
<div align="center">
<div align="center">
  <img src=".assets/lychee-banner.png" alt="Uma lichia gigante no centro de uma explosão de frutas em estilo ilustrado." />
</div>
<h3 align="center">Lychee</h3>

  <p align="center">
    O Gerenciador de monorepos poliglota para desenvolvimento "Contract-First"
    <br />
    <br />
    <a href="#"><strong>Site Oficial »</strong></a>
    <br />
    <br />
    <a href="https://github.com/jovemexausto/lychee">GitHub</a>
    ·
    <a href="https://github.com/jovemexausto/lychee/issues">Report Bug</a>
  </p>
</div>

## Sobre o Projeto

**Lychee** é uma ferramenta de interface de linha de comando (CLI) projetada para simplificar e acelerar o desenvolvimento em monorepos poliglota. Ao adotar uma filosofia **"schema-first"**, Lychee transforma sua coleção de serviços em um aplicativo único e coeso, proporcionando uma experiência de desenvolvedor (DX) incomparável, guiada pelo princípio de **"Zero Context Switching"**.

Pare de fazer malabarismos com vários terminais, lutar com variáveis de ambiente e depurar incompatibilidades de contratos de API. Lychee cuida da orquestração para que você possa se concentrar na construção de funcionalidades.

---

## 🍅 O Problema Central que o Lychee Resolve

Microsserviços e monorepos oferecem poderosos benefícios arquitetônicos, mas introduzem uma complexidade significativa:

- **Sobrecarga Cognitiva**: Gerenciar vários serviços, cada um com sua própria linguagem e ferramentas, leva a uma constante troca de contexto.
- **Inferno da Integração**: Contratos de API incompatíveis entre serviços resultam em código frágil e erros em tempo de execução.
- **Feedback Lento**: Uma pequena mudança em um modelo de dados compartilhado pode exigir uma reconstrução e reinício completos de vários serviços.

---

## 🥭 Como o Lychee Oferece um DX Delicioso

Lychee aborda esses desafios com um conjunto de recursos integrados, todos controlados a partir de uma única CLI. O foco está no "Core DX Loop" impulsionado pelo comando `lx dev`, que fornece um ciclo de feedback contínuo e rápido.

### 🍊 1. Desenvolvimento "Schema-First"

- Defina seus contratos de dados uma única vez usando um esquema central (por exemplo, JSON Schema).
- Gera automaticamente código nativo e com segurança de tipos para seus serviços.
- Mantém front-ends em TypeScript e back-ends em Python sincronizados.
- Elimina uma classe enorme de bugs de integração antes mesmo que eles aconteçam.

### 🍓 2. O Painel de Desenvolvimento Unificado

O comando `lx dev` lança uma interface de usuário de terminal (TUI) bonita e em tempo real, baseada em `Rich`, que fornece um painel único para todo o seu monorepo.

- **Status do Serviço**: Veja quais serviços estão em execução, sendo reconstruídos ou falharam, com indicadores como `RUNNING`, `STARTING` ou `ERROR`.
- **Logs em Tempo Real**: Agregue e codifique logs por cores de todos os serviços em um só lugar, capturando `stdout` e `stderr`.
- **Sincronização de Esquema**: Observe o status de seus contratos de dados à medida que são gerados automaticamente.
- **Verificações de Saúde**: Lychee relata a saúde de cada serviço, para que você saiba exatamente quando ele está pronto.

### 🍋 3. Orquestração Inteligente e "Hot Reloading"

Lychee entende o gráfico de dependências do seu projeto.

- **Inicialização Inteligente**: Inicie todo o seu aplicativo com um único comando (`lx dev`). Os serviços iniciam na ordem correta, aguardando verificações de saúde.
- **"Hot Reloading" Cirúrgico**: Mudanças no código ou no esquema acionam reinícios apenas para os serviços afetados, com um observador de arquivos monitorando alterações em esquemas (`*.schema.json`) ou código-fonte.
- Permite ciclos de feedback extremamente rápidos, mesmo em projetos grandes, refletindo mudanças no painel em tempo real.

### 🍍 4. Poliglota por Natureza

- Construído em torno de um sistema de plugins.
- Funciona perfeitamente com diferentes linguagens e frameworks.
- Suporta inicialmente Python (Pydantic) e TypeScript (Zod).
- Facilmente extensível para Go, Rust, C++, e muito mais, com plugins instaláveis via pacotes (ex: pip).

### 🥑 5. Onboarding e Colaboração Simplificados

- Novos desenvolvedores podem ter um ambiente de desenvolvimento completo funcionando em minutos.
- Um único comando `lx onboard` cuida de:
  - Instalação de dependências
  - Seeding de dados
  - Configuração do ambiente
- **Inicialização de Pacotes e Serviços**: Use `lx new` para scaffolding a partir de templates, como `lx new service my-new-service --template python-fastapi`, que cria estruturas, configura `lychee.yaml` e instala dependências automaticamente.

### 🍇 6. Primitivas Integradas do Lychee

Lychee oferece "primitivas" schema-driven para padrões comuns, como filas, hooks e stores chave-valor.

- **Exemplo**: `lx add queue notification-events` gera esquemas e código tipado para produtores e consumidores.
- Integra-se ao gerenciador de esquemas para tipo-seguro em múltiplas linguagens.

### 🥝 7. Integração Completa com Docker

- **Desenvolvimento Containerizado**: `lx dev` pode executar serviços em containers via `docker-compose` para ambientes consistentes.
- **Geração Automática de Dockerfile**: Templates incluem Dockerfiles prontos.
- **Build e Deploy**: Comandos como `lx build --platform docker` e `lx deploy` para imagens e registries.

### 🍉 8. Controle Total sobre Variáveis de Ambiente

- **Hierarquia de Configuração**: Defina variáveis globais, por serviço ou por ambiente em arquivos como `lychee.yaml` ou `.monorepo/environments/staging.yml`.
- **Gerenciamento de Segredos**: Use `.lychee.env` para valores sensíveis, carregados automaticamente e ignorados no Git.

---

## 🚀 Lychee: Menos Gerenciamento, Mais Criação

Lychee não é apenas uma ferramenta de construção; é um **ambiente de desenvolvimento**. Ele unifica seus serviços, impõe seus contratos e automatiza seus fluxos de trabalho—permitindo que sua equipe construa mais rápido e com mais confiança.

---

## 🗺️ Roadmap do Projeto

Aqui você encontra o progresso atual e os próximos passos para o Lychee. Estamos comprometidos em oferecer a melhor experiência de desenvolvimento em monorepos, priorizando o "Core DX Loop" para valor imediato.

### ✅ Concluído

- [x] **Hello World**: Funcionalidade básica para iniciar e testar o Lychee.
- [x] **Iniciação de Serviços**: Comando único (`lx dev start`) para iniciar todos os serviços do monorepo.
- [x] **Descoberta de Serviços**: Configuração via `service.yml` como fonte única da verdade para descoberta, versão Python e mais.
- [x] **Logs Agregados**: Visualização unificada e colorida de logs de todos os serviços.
- [x] **Gerenciamento de Versão Python**: Uso correto da versão Python especificada por serviço via `service.yml`.
- [x] **Compartilhamento de Schemas**: Geração e compartilhamento de schemas compilados via symlink.
- [x] **Inicialização de Monorepo**: Criação de novos monorepos a partir de templates.
- [x] **Geração de Pydantic**: Geração automática de modelos Pydantic a partir de JSON Schemas.

### ⏳ Em Andamento

- [ ] **Suporte a TypeScript e Tipagem Segura**: Implementação completa do suporte a TypeScript, garantindo a compilação de tipos seguros para ambos os lados (front-end e back-end).
- [ ] **Tratamento de Erros para Linguagens Não Suportadas**: Adicionar feedback claro e mensagens de erro informativas ao tentar adicionar linguagens não suportadas.
- [ ] **Gerenciamento Inteligente de Symlinks**: Ao alterar um symlink, remover automaticamente o antigo e verificar a integridade dos symlinks existentes.
- [ ] **Integração com `.gitignore`**: Adicionar automaticamente diretórios de montagem (`mount_dir`) ao arquivo `.gitignore` para evitar commits acidentais.
- [ ] **Sistema de Plugins e Hooks**: Implementar um sistema robusto de plugins e hooks (ex: `on_start`, `on_stop`, `before_this`, `after_that`) para maior extensibilidade.
- [ ] **Plugins para Linguagens, Docker e Ferramentas**: Permitir que linguagens, ferramentas de build e templates sejam gerenciados como plugins, instaláveis via pacotes (ex: pip).
- [ ] **Autoinstalação e Carregamento de Plugins**: Lychee deve ser capaz de auto-instalar e carregar plugins listados no `lychee.yml`.
- [ ] **Gerenciamento de Entidades**: Introduzir conceitos como `services`, `packages`, `tools`, `resources` para uma melhor organização do monorepo.
- [ ] **Comando `init` Aprimorado**: Tornar o comando `init` mais agradável, simples e flexível, permitindo a criação de projetos em branco ou a inicialização no diretório atual.
- [ ] **Comando `new` para Templates**: Introduzir o comando `lx new` para criar projetos, serviços ou schemas a partir de templates de forma intuitiva (ex: `lx new service -l python312 --from flask-auth-api`).

### 🔮 Próximos Passos

- [ ] **Primitives do Lychee**: Introduzir queues, hooks, KV stores e mais, com geração schema-driven de código tipado (ex: `lychee add queue notification-events`).
- [ ] **Integração Profunda com Docker**: Suporte completo para desenvolvimento containerizado, geração automática de Dockerfiles e comandos de build/deploy.
- [ ] **Controle Avançado de Variáveis de Ambiente**: Hierarquia de configuração e gerenciamento de segredos com `.lychee.env`.
- [ ] **Proxy Simples Integrado**: Adicionar um proxy reverso in-process para roteamento de tráfego local durante o desenvolvimento.
- [ ] **Testes Integrados e Correlação de Erros**: Adicionar suporte para testes automatizados e análise avançada de erros no painel.
- [ ] **Assistência de IA**: Integrar sugestões inteligentes para depuração e otimização baseadas no contexto do monorepo.
