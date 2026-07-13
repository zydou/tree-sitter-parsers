import XCTest
import SwiftTreeSitter
import TreeSitterSnl

final class TreeSitterSnlTests: XCTestCase {
    func testCanLoadGrammar() throws {
        let parser = Parser()
        let language = Language(language: tree_sitter_snl())
        XCTAssertNoThrow(try parser.setLanguage(language),
                         "Error loading Snl grammar")
    }
}
