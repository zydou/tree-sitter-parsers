package tree_sitter_sproto_test

import (
	"testing"

	tree_sitter "github.com/tree-sitter/go-tree-sitter"
	tree_sitter_sproto "github.com/hanxi/tree-sitter-sproto/bindings/go"
)

func TestCanLoadGrammar(t *testing.T) {
	language := tree_sitter.NewLanguage(tree_sitter_sproto.Language())
	if language == nil {
		t.Errorf("Error loading sproto grammar")
	}
}
