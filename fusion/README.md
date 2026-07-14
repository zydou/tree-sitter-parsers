# tree-sitter-fusion

This is a [tree-sitter](https://github.com/tree-sitter/tree-sitter)
grammar for [Fusion](https://docs.neos.io/cms/manual/rendering/fusion),
a declarative language, designed for rendering purposes in
[Neos CMS](https://neos.io).

## Usage with neovim
This grammer is part of [nvim-treesitter](https://github.com/nvim-treesitter/nvim-treesitter). 
Therefore usage within neovim is simple, see the [README.md](https://github.com/nvim-treesitter/nvim-treesitter#installation) for details.

## Contribute
If you want to contribute to this repository - Great Idea - and thank
you at this point.
See [Contribtion Guide](./CONTRIBUTING.md) for details.

## Develop
This is a [tree-sitter](https://tree-sitter.github.io/tree-sitter/) grammar, see the documentation for details.

### Install
Download or checkout this repository and install the
dependencies.

```sh
git clone git@gitlab.com:jirgn/tree-sitter-fusion.git 
cd tree-sitter-fusion 
yarn install
```

### Test
We have an extensive test-suite to ensure, the grammar works as
exprected. 
Run tests with the following command

```sh
yarn test
```

### Playground
Treesitter ships with an Playground Interface to easily explore
the behaviour of our grammar.
You will need [Docker](https://www.docker.com/) or a compatible
container command for this to work.
You can start the playground with the following command

```sh
systemctl start docker
yarn playground
```

## Relevant Resources / Inspirations
Because of the lack of specifications, I had to look at some other
grammars and the implementation to write this code. If you want to
contribute maybe the following resources are helpful
* [Fusion
  Parser](https://github.com/neos/neos-development-collection/blob/master/Neos.Fusion/Classes/Core/Parser.php)
* [IntelliJ Neos
  Grammar](https://github.com/cvette/intellij-neos/tree/main/src/main/grammars)
* [Eel
  PEG Grammar](https://github.com/neos/flow-development-collection/blob/master/Neos.Eel/Resources/Private/Grammar/Eel.peg.inc)
* [tree-sitter-javascript](https://github.com/tree-sitter/tree-sitter-javascript)

