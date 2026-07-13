import XCTest
import SwiftTreeSitter
import TreeSitterSproto

final class TreeSitterSprotoTests: XCTestCase {
    func testCanLoadGrammar() throws {
        let parser = Parser()
        let language = Language(language: tree_sitter_sproto())
        XCTAssertNoThrow(try parser.setLanguage(language),
                         "Error loading sproto grammar")
    }
}
