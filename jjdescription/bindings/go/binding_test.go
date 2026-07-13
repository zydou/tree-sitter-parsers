package tree_sitter_jjdescription_test

import (
	"testing"

	tree_sitter "github.com/tree-sitter/go-tree-sitter"
	tree_sitter_jjdescription "github.com/tree-sitter/tree-sitter-jjdescription/bindings/go"
)

func TestCanLoadGrammar(t *testing.T) {
	language := tree_sitter.NewLanguage(tree_sitter_jjdescription.Language())
	if language == nil {
		t.Errorf("Error loading JJ Description grammar")
	}
}
