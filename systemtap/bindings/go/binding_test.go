package tree_sitter_systemtap_test

import (
	"testing"

	tree_sitter "github.com/smacker/go-tree-sitter"
	"github.com/ok-ryoko/tree-sitter-systemtap"
)

func TestCanLoadGrammar(t *testing.T) {
	language := tree_sitter.NewLanguage(tree_sitter_systemtap.Language())
	if language == nil {
		t.Errorf("Error loading SystemTap grammar")
	}
}
