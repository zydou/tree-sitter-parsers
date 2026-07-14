## [1.1.2](https://gitlab.com/jirgn/tree-sitter-fusion/compare/v1.1.1...v1.1.2) (2021-12-29)


### Bug Fixes

* tweak grammar for more easy quering ([40349c6](https://gitlab.com/jirgn/tree-sitter-fusion/commit/40349c694f04bb06f29bd1f9300d80e422a06189))

## [1.1.1](https://gitlab.com/jirgn/tree-sitter-fusion/compare/v1.1.0...v1.1.1) (2021-12-21)


### Bug Fixes

* allow -_ in afx identifiers (attributes and names) ([cdd1880](https://gitlab.com/jirgn/tree-sitter-fusion/commit/cdd18807f8504a65000f2f3e7c5db0bf2bd794a6))
* introduce afx_statement to allow text and expression top level elements ([a67b244](https://gitlab.com/jirgn/tree-sitter-fusion/commit/a67b244cf99b9898d3dd597de0ef8fe91b2541ea))
* simplified afx attribute and update highlights ([0204a99](https://gitlab.com/jirgn/tree-sitter-fusion/commit/0204a996f42558d9251d58b54fe167f94893f845))
* typo in afx highlight groups ([0b45b83](https://gitlab.com/jirgn/tree-sitter-fusion/commit/0b45b83346304b0f05b26cfddf5269d09732d4df))

# [1.1.0](https://gitlab.com/jirgn/tree-sitter-fusion/compare/v1.0.3...v1.1.0) (2021-12-20)


### Features

* add afx support ([c459f58](https://gitlab.com/jirgn/tree-sitter-fusion/commit/c459f580700b54a39b871228acfa0c5b1ab9ac3e)), closes [#2](https://gitlab.com/jirgn/tree-sitter-fusion/issues/2)

## [1.0.3](https://gitlab.com/jirgn/tree-sitter-fusion/compare/v1.0.2...v1.0.3) (2021-12-07)


### Bug Fixes

* dummy to bump version and release npm package ([c2ef0f2](https://gitlab.com/jirgn/tree-sitter-fusion/commit/c2ef0f267fcc2285e314984ab0cda843e187ca9e))

## [1.0.2](https://gitlab.com/jirgn/tree-sitter-fusion/compare/v1.0.1...v1.0.2) (2021-12-05)


### Bug Fixes

* add eel binary expressions for comparison ([4e9ce37](https://gitlab.com/jirgn/tree-sitter-fusion/commit/4e9ce374a2d3282c0e5f09486d9242e51562acf9))
* allow : in object path ([a9d92ad](https://gitlab.com/jirgn/tree-sitter-fusion/commit/a9d92ad0e5c83d3263e4b4d884f1542a557428f1))
* allow string keys as property ([d24ac41](https://gitlab.com/jirgn/tree-sitter-fusion/commit/d24ac417290687faf261fdee528c374699ae7642))
* allow type- and package-names with numbers ([4fe0e73](https://gitlab.com/jirgn/tree-sitter-fusion/commit/4fe0e73f1f6bf1aaa5ae2a36ffd4065c94394632))
* dsl identifier can have digits and dots ([de051e9](https://gitlab.com/jirgn/tree-sitter-fusion/commit/de051e911d9adf4ec5819471bf10008a0d5b8046))
* filglobbing could be without .fusion extension ([70a1514](https://gitlab.com/jirgn/tree-sitter-fusion/commit/70a151409cadd05a9d95e947e953501abcdabc0c))
* namespace syntax ([44ce6df](https://gitlab.com/jirgn/tree-sitter-fusion/commit/44ce6dfe32cb67faa7953bb72558108b86490098))
* path_part could also be a 1 digit number ([32ba4d3](https://gitlab.com/jirgn/tree-sitter-fusion/commit/32ba4d3bed8ca3e3aab4033d92a17b88078e1bf0))
* rename identifier for more consistency ([cf38a1c](https://gitlab.com/jirgn/tree-sitter-fusion/commit/cf38a1ca3e35a11396945d3b6abc7664d0fbcf8e))

## [1.0.1](https://gitlab.com/jirgn/tree-sitter-fusion/compare/v1.0.0...v1.0.1) (2021-11-26)


### Bug Fixes

* align highlight groups to match nvim-treesitter spec ([66e7bde](https://gitlab.com/jirgn/tree-sitter-fusion/commit/66e7bde856f2d71a1fc96aafd3ac020ffc4ab2f1))
* typo in highlight group punct(u)ation ([144dfb8](https://gitlab.com/jirgn/tree-sitter-fusion/commit/144dfb81237861dd155d005d8bc954b1989ad7fb))

# 1.0.0 (2021-11-26)


### Bug Fixes

* add missing test ([e1aabb0](https://gitlab.com/jirgn/tree-sitter-fusion/commit/e1aabb04c64d107d0cdc4cf7c788c2230a3b8174))
* add tests for complex property ([da8def3](https://gitlab.com/jirgn/tree-sitter-fusion/commit/da8def3d49e5a6c60454068e3e7da03bd86d08d6))
* better object type ([378b0f5](https://gitlab.com/jirgn/tree-sitter-fusion/commit/378b0f529e764f471952bc6173e8b568a31a39e1))
* move comment from extras to prog so include does not break ([b9da5fc](https://gitlab.com/jirgn/tree-sitter-fusion/commit/b9da5fc32bae9e9ac3b37c6043fbcfe7026a75ce))
* remove unnecessary token statements ([07bf099](https://gitlab.com/jirgn/tree-sitter-fusion/commit/07bf099826ed633397fe9299d8bf323a54df9ff1))
* value string with escaped php path like "some\\path" ([c543932](https://gitlab.com/jirgn/tree-sitter-fusion/commit/c5439328536e8fbc534e2e1932b34c6cc8d09b8d))


### Features

* add hightlight for tokens and allow prototype as protpery name ([a3570ac](https://gitlab.com/jirgn/tree-sitter-fusion/commit/a3570ac5bbfe5038b25f614c2dd3820e31170faa))
* add property block ([4ca9e1b](https://gitlab.com/jirgn/tree-sitter-fusion/commit/4ca9e1baba9c5c85c942072b172571757b72f6e7))
* add property deletion ([8e4b6e4](https://gitlab.com/jirgn/tree-sitter-fusion/commit/8e4b6e44cd2bca8b9b31262afdbbf821264c8092))
* add string primitives ([5689c2e](https://gitlab.com/jirgn/tree-sitter-fusion/commit/5689c2e3b1de1b1cf96da332d3b0e9d1da20f7a7))
* basic syntax highlight ([520aeac](https://gitlab.com/jirgn/tree-sitter-fusion/commit/520aeacc452647aeb70e16599c1dfe2b2fca1045))
* first definitions ([bdf6ac7](https://gitlab.com/jirgn/tree-sitter-fusion/commit/bdf6ac7301ab5b2f514aa57400b0145776276a74))
* property copy (simple) ([bbec25c](https://gitlab.com/jirgn/tree-sitter-fusion/commit/bbec25c8970d7a3cbbcea7912fa53806f873eaed))
* prototype copy ([cec8360](https://gitlab.com/jirgn/tree-sitter-fusion/commit/cec836024b707ba2dfc4fa70de9021a18638bb5a))
* prototype instance assign ([459a59b](https://gitlab.com/jirgn/tree-sitter-fusion/commit/459a59b3055fc799e17a8ebb8818d2be523670d9))
