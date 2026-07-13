package tree_sitter_kos_test

import (
	"testing"

	tree_sitter "github.com/tree-sitter/go-tree-sitter"
	tree_sitter_kos "github.com/tree-sitter/tree-sitter-Kos/bindings/go"
)

func TestCanLoadGrammar(t *testing.T) {
	language := tree_sitter.NewLanguage(tree_sitter_kos.Language())
	if language == nil {
		t.Errorf("Error loading Kos grammar")
	}
}
