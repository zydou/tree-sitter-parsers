import XCTest
import SwiftTreeSitter
import TreeSitterKos

final class TreeSitterKosTests: XCTestCase {
    func testCanLoadGrammar() throws {
        let parser = Parser()
        let language = Language(language: tree_sitter_kos())
        XCTAssertNoThrow(try parser.setLanguage(language),
                         "Error loading Kos grammar")
    }
}
