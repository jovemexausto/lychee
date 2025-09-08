<div align="center">
  <img src=".assets/lychee-banner.png" alt="Uma lichia gigante no centro de uma explosão de frutas em estilo ilustrado." />
</div>

# Lychee: O Gerenciador de Monorepo Poliglota para Desenvolvimento "Contract-First"

**Lychee** é uma ferramenta de interface de linha de comando (CLI) projetada para simplificar e acelerar o desenvolvimento em monorepos poliglota. Ao adotar uma filosofia **"schema-first"**, Lychee transforma sua coleção de serviços em um aplicativo único e coeso, proporcionando uma experiência de desenvolvedor (DX) incomparável.

Pare de fazer malabarismos com vários terminais, lutar com variáveis de ambiente e depurar incompatibilidades de contratos de API. Lychee cuida da orquestração para que você possa se concentrar na construção de funcionalidades.

---

## 🍅 O Problema Central que o Lychee Resolve

Microsserviços e monorepos oferecem poderosos benefícios arquitetônicos, mas introduzem uma complexidade significativa:

- **Sobrecarga Cognitiva**: Gerenciar vários serviços, cada um com sua própria linguagem e ferramentas, leva a uma constante troca de contexto.
- **Inferno da Integração**: Contratos de API incompatíveis entre serviços resultam em código frágil e erros em tempo de execução.
- **Feedback Lento**: Uma pequena mudança em um modelo de dados compartilhado pode exigir uma reconstrução e reinício completos de vários serviços.

---

## 🥭 Como o Lychee Oferece um DX Delicioso

Lychee aborda esses desafios com um conjunto de recursos integrados, todos controlados a partir de uma única CLI.

### 🍊 1. Desenvolvimento "Schema-First"

- Defina seus contratos de dados uma única vez usando um esquema central (por exemplo, JSON Schema).
- Gera automaticamente código nativo e com segurança de tipos para seus serviços.
- Mantém front-ends em TypeScript e back-ends em Python sincronizados.
- Elimina uma classe enorme de bugs de integração antes mesmo que eles aconteçam.

### 🍓 2. O Painel de Desenvolvimento Unificado

O comando `lychee dev` lança uma interface de usuário de terminal (TUI) bonita e em tempo real que fornece um painel único para todo o seu monorepo.

- **Status do Serviço**: Veja quais serviços estão em execução, sendo reconstruídos ou falharam.
- **Logs em Tempo Real**: Agregue e codifique logs por cores de todos os serviços em um só lugar.
- **Sincronização de Esquema**: Observe o status de seus contratos de dados à medida que são gerados automaticamente.
- **Verificações de Saúde**: Lychee relata a saúde de cada serviço, para que você saiba exatamente quando ele está pronto.

### 🍋 3. Orquestração Inteligente e "Hot Reloading"

Lychee entende o gráfico de dependências do seu projeto.

- **Inicialização Inteligente**: Inicie todo o seu aplicativo com um único comando (`lychee dev`). Os serviços iniciam na ordem correta.
- **"Hot Reloading" Cirúrgico**: Mudanças no código ou no esquema acionam reinícios apenas para os serviços afetados.
- Permite ciclos de feedback extremamente rápidos, mesmo em projetos grandes.

### 🍍 4. Poliglota por Natureza

- Construído em torno de um sistema de plugins.
- Funciona perfeitamente com diferentes linguagens e frameworks.
- Suporta inicialmente Python (Pydantic) e TypeScript (Zod).
- Facilmente extensível para Go, Rust, C++, e muito mais.

### 🥑 5. Onboarding e Colaboração Simplificados

- Novos desenvolvedores podem ter um ambiente de desenvolvimento completo funcionando em minutos.
- Um único comando `lychee onboard` cuida de:
  - Instalação de dependências
  - Seeding de dados
  - Configuração do ambiente

---

## 🚀 Lychee: Menos Gerenciamento, Mais Criação

Lychee não é apenas uma ferramenta de construção; é um **ambiente de desenvolvimento**. Ele unifica seus serviços, impõe seus contratos e automatiza seus fluxos de trabalho—permitindo que sua equipe construa mais rápido e com mais confiança.
