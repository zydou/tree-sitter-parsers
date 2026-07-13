package tree_sitter_snl_test

import (
	"testing"

	tree_sitter "github.com/tree-sitter/go-tree-sitter"
	tree_sitter_snl "github.com/minijackson/tree-sitter-snl/bindings/go"
)

func TestCanLoadGrammar(t *testing.T) {
	language := tree_sitter.NewLanguage(tree_sitter_snl.Language())
	if language == nil {
		t.Errorf("Error loading Snl grammar")
	}
}
