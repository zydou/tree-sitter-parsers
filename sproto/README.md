# tree-sitter-sproto

[![GitHub](https://img.shields.io/badge/github-hanxi%2Ftree--sitter--sproto-blue)](https://github.com/hanxi/tree-sitter-sproto)

> **Treesitter for sproto**

This repository provides a [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar for the [sproto](https://github.com/cloudwu/sproto) serialization protocol. With this grammar, you can enable advanced syntax highlighting, code folding, and structural analysis for sproto files in editors and tools that support Tree-sitter, such as Neovim (via nvim-treesitter).

## Features

- Syntax highlighting for sproto files.
- Tree-sitter queries for advanced code navigation.
- Multi-language bindings (Node.js, Python, Rust, Go, Swift).
- Easily integratable with editor plugins (like nvim-treesitter).

## Getting Started

### Requirements

- [Node.js](https://nodejs.org/) (for development and testing)
- [Tree-sitter CLI](https://tree-sitter.github.io/tree-sitter/creating-parsers#installation)
- Your preferred editor with Tree-sitter support (e.g., Neovim)

### Installation

#### For Neovim (via nvim-treesitter)

Add `tree-sitter-sproto` to your `nvim-treesitter` configuration:

```lua
require'nvim-treesitter.parsers'.get_parser_configs().sproto = {
  install_info = {
    url = "https://github.com/hanxi/tree-sitter-sproto",
    files = {"src/parser.c"}
  },
  filetype = "sproto",
}
```

#### Building Locally

Clone the repository and build the parser:

```bash
git clone https://github.com/hanxi/tree-sitter-sproto.git
cd tree-sitter-sproto
npm install
npm run build
```

### Usage

After building, you can use the generated parser in any tool that accepts Tree-sitter grammars. For editor integration, follow the instructions of the relevant plugin.

## Development

- Grammar is defined in [`grammar.js`](./grammar.js)
- See `tree-sitter.json` for parser configuration.
- Multiple build systems supported: `Makefile`, `CMakeLists.txt`, `Cargo.toml`, `setup.py`, `go.mod`, `Package.swift`.

To generate parser source files:

```bash
npx tree-sitter generate
```

## Contributing

Contributions are welcome! Please create issues or PRs if you find bugs or want to improve the grammar.

## License

MIT or same as Tree-sitter (see LICENSE if present).

## Links

- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [sproto Documentation](https://github.com/cloudwu/sproto)
