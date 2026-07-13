# tree-sitter-groq

A [Tree-sitter](https://tree-sitter.github.io/) parser for the [GROQ](https://groq.dev/) query language.

## About GROQ

GROQ (Graph-Relational Object Queries) is a declarative query language developed by [Sanity.io](https://www.sanity.io/) for filtering and projecting JSON documents. It's designed to be intuitive and powerful, allowing you to query structured content with a syntax that feels natural for working with document databases.

GROQ enables you to:
- Filter documents based on complex conditions
- Project specific fields from your data
- Transform and reshape query results
- Navigate relationships between documents

## Installation

```bash
npm install tree-sitter-groq
```

## Usage

### Node.js

```javascript
const Parser = require('tree-sitter');
const Groq = require('tree-sitter-groq');

const parser = new Parser();
parser.setLanguage(Groq);

const code = `*[_type == "post" && publishedAt < now()]{title, slug, publishedAt}`;
const tree = parser.parse(code);
console.log(tree.rootNode.toString());
```

### Python

```python
import tree_sitter_groq as tsgroq
from tree_sitter import Language, Parser

GROQ_LANGUAGE = Language(tsgroq.language())

parser = Parser(GROQ_LANGUAGE)
code = b'*[_type == "post"]{title, body}'
tree = parser.parse(code)
print(tree.root_node.sexp())
```

### Rust

Add this to your `Cargo.toml`:

```toml
[dependencies]
tree-sitter-groq = "1.0"
```

```rust
use tree_sitter::{Language, Parser};

extern "C" { fn tree_sitter_groq() -> Language; }

fn main() {
    let mut parser = Parser::new();
    parser.set_language(unsafe { tree_sitter_groq() }).unwrap();
    
    let code = r#"*[_type == "author"]{name, "postCount": count(*[_type == "post" && references(^._id)])}"#;
    let tree = parser.parse(code, None).unwrap();
    println!("{}", tree.root_node().to_sexp());
}
```

## Development

```bash
# Install dependencies
npm install

# Generate parser
tree-sitter generate

# Test the parser
npm test

# Try the playground
npm start
```

## Language Support

This parser supports the full GROQ language specification, including:

- Document filtering (`*[condition]`)
- Field projection (`{field1, field2}`)
- Functions and operators
- Nested queries and projections
- String interpolation
- Array and object slicing
- Conditional expressions

## Resources

- [GROQ Language Documentation](https://groq.dev/)
- [Tree-sitter Documentation](https://tree-sitter.github.io/)
- [Sanity.io](https://www.sanity.io/)
- [GROQ Language Specification](https://groq.dev/spec)

## License

MIT