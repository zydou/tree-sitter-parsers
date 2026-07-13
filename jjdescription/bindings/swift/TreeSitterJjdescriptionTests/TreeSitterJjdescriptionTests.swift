import XCTest
import SwiftTreeSitter
import TreeSitterJjdescription

final class TreeSitterJjdescriptionTests: XCTestCase {
    func testCanLoadGrammar() throws {
        let parser = Parser()
        let language = Language(language: tree_sitter_jjdescription())
        XCTAssertNoThrow(try parser.setLanguage(language),
                         "Error loading JJ Description grammar")
    }
}
