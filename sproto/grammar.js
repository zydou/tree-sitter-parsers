module.exports = grammar({
  name: 'sproto',

  extras: $ => [
    /\s/,
    $.comment,
  ],

  rules: {
    source_file: $ => repeat(
      choice(
        $.type_definition,
        $.protocol_definition
      )
    ),

    comment: $ => /#.*/,

    // =============================================
    // Type definition with nested types support
    // =============================================
    type_definition: $ => seq(
      '.',
      field('name', $.identifier),
      '{',
      repeat(
        choice(
          $.field_definition,
          $.nested_type_definition  // 分开处理嵌套类型
        )
      ),
      '}'
    ),

    // 专门处理嵌套类型定义
    nested_type_definition: $ => seq(
      '.',
      field('name', $.identifier),
      '{',
      repeat($.field_definition),
      '}'
    ),

    field_definition: $ => seq(
      field('name', $.identifier),
      field('tag', $.integer),
      ':',
      optional(field('is_array', '*')),
      field('type', $.type_specifier),
      optional(
        choice(
          field('map_key_type', $.map_specifier),
          field('fixed_point', $.fixed_point_specifier)
        )
      )
    ),

    type_specifier: $ => choice(
      'string',
      'integer',
      'boolean',
      'binary',
      'double',
      $.identifier
    ),

    map_specifier: $ => seq(
      '(',
      field('key', $.identifier),
      ')'
    ),

    fixed_point_specifier: $ => seq(
      '(',
      field('precision', $.integer),
      ')'
    ),

    // =============================================
    // Protocol definition
    // =============================================
    protocol_definition: $ => seq(
      field('name', $.identifier),
      field('tag', $.integer),
      '{',
      repeat(
        choice(
          $.request_block,
          $.response_block,
          $.type_definition
        )
      ),
      '}'
    ),

    request_block: $ => seq(
      'request',
      choice(
        field('type', $.type_specifier),  // 直接类型引用
        seq(                              // 完整请求定义
          '{',
          repeat($.field_definition),
          '}'
        )
      )
    ),

    response_block: $ => seq(
      'response',
      choice(
        field('type', $.type_specifier),  // 直接类型引用
        seq(                              // 完整响应定义
          '{',
          repeat($.field_definition),
          '}'
        )
      )
    ),

    // =============================================
    // Basic Tokens
    // =============================================
    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_]*/,
    integer: $ => /\d+/,
  }
});
