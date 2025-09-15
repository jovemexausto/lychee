.
├── examples
│   └── hello-world
│   ├── lychee.yaml
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── README.md
│   ├── schemas
│   │   ├── customer.schema.json
│   │   └── message.schema.json
│   └── services
│   ├── bar
│   │   ├── main.py
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   ├── service.yaml
│   │   └── uv.lock
│   └── foo
│   ├── main.py
│   ├── pyproject.toml
│   ├── README.md
│   ├── service.yaml
│   └── uv.lock
├── justfile
├── lychee-cli
│   ├── pyproject.toml
│   ├── README.md
│   └── src
│   └── lychee
│   └── cli
│   ├── commands
│   │   ├── dev.py
│   │   ├── init.py
│   │   ├── install.py
│   │   ├── new.py
│   │   └── schema.py
│   ├── **init**.py
│   ├── main.py
│   └── middleware
│   └── error_handler.py
├── lychee-core
│   ├── pyproject.toml
│   ├── README.md
│   └── src
│   └── lychee
│   └── core
│   ├── config
│   │   ├── **init**.py
│   │   ├── loader.py
│   │   ├── merger.py
│   │   └── models.py
│   ├── **init**.py
│   ├── languages
│   │   ├── adapter.py
│   │   ├── python.py
│   │   └── registry.py
│   ├── project.py
│   ├── schema
│   │   ├── manager.py
│   │   ├── validator.py
│   │   └── watcher.py
│   ├── server
│   │   └── development.py
│   ├── service.py
│   ├── templates
│   │   ├── manager.py
│   │   └── templates
│   │   └── basic
│   │   ├── lychee.yaml
│   │   ├── package.json
│   │   ├── pnpm-lock.yaml
│   │   ├── README.md
│   │   ├── schemas
│   │   │   ├── customer.schema.json
│   │   │   └── message.schema.json
│   │   └── services
│   │   ├── fastapi
│   │   │   ├── main.py
│   │   │   ├── pyproject.toml
│   │   │   ├── README.md
│   │   │   ├── service.yaml
│   │   │   └── uv.lock
│   │   └── run_file
│   │   ├── main.py
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   ├── service.yaml
│   │   └── uv.lock
│   └── utils
│   ├── fs.py
│   ├── **init**.py
│   ├── logging.py
│   └── process.py
├── pyproject.toml
├── README.md
├── TODO.md
└── uv.lock

29 directories, 68 files
