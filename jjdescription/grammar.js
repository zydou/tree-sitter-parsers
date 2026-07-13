/**
 * @file Tree-sitter parser for `jj desc` buffers.
 * @author Riley Bruins <ribru17@gmail.com>
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

const NEWLINE = /\r?\n/;
const ANYTHING = /[^\r\n]+/;
const TEXT = /[^J\r\n].*|J[^J\r\n].*|JJ[^:\r\n].*|J|JJ/;

module.exports = grammar({
  name: 'jjdescription',

  extras: (_) => [],

  externals: (
    $,
  ) => [
    $._change_id,
    $._diff_summary,
    $._subject,
    $._error_sentinel,
  ],

  rules: {
    source: ($) =>
      seq(
        repeat(choice(NEWLINE, $.comment, $.generated_comment)),
        optional(
          seq(
            $.subject,
            repeat(
              choice($.body_line, NEWLINE, $.comment, $.generated_comment),
            ),
          ),
        ),
        optional($.ignore_rest),
      ),

    comment: ($) =>
      prec.right(
        seq(
          'JJ:',
          optional(alias(ANYTHING, $.comment_content)),
          optional(NEWLINE),
        ),
      ),

    subject: ($) =>
      prec.right(
        seq(
          choice(
            seq($.prefix, optional(ANYTHING)),
            $._subject,
          ),
          optional(NEWLINE),
        ),
      ),

    prefix: ($) =>
      choice(
        seq(
          /[ \t\f\v]*/,
          $.type,
          optional(seq('(', $.scope, ')')),
          optional('!'),
          alias(/[:\uff1a]/, ':'),
        ),
      ),

    type: (_) => /\w+/,

    scope: (_) => /[^\r\n)]+/,

    body_line: (_) => prec.right(seq(TEXT, optional(NEWLINE))),

    ignore_rest: ($) =>
      seq('JJ: ignore-rest', optional(seq(NEWLINE, optional($.rest)))),

    rest: (_) => /[\s\S]+/,

    generated_comment: ($) =>
      choice(
        seq($._change_id, $.change_id, NEWLINE),
        seq(
          $._diff_summary,
          choice('A', 'M', 'D', 'C', 'R'),
          / /,
          $.filepath,
          NEWLINE,
        ),
      ),

    change_id: (_) => /[k-z]+/,

    filepath: (_) => ANYTHING,
  },
});
