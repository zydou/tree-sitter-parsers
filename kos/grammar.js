module.exports = grammar({
  name: 'kos',

  word: $ => $.identifier,

  extras: $ => [
    $.comment,
    $._whitespace,
    $._eol
  ],

  precedences: _ => [
    [
      'with',
      'parameters',
      'refinement',
      'invocation',
      'primary',
      'member',
      'unary',
      'multiplication',
      'addition',
      'bitwise',
      'comparison',
      'logical',
      'binary',
      'conditional',
      'stream',
      'yield'
    ]
  ],

  rules: {
    source_file: $ => seq(
      optional($.hash_bang),
      repeat(prec(2, choice($.import, ';'))),
      repeat(prec(1, choice($._statement, $.public_statement, ';')))
    ),

    hash_bang: _ => /#!.*/,

    import: $ => prec.left(seq(
      'import',
      field('path', repeat(seq($.identifier, '/'))),
      field('module', $.identifier),
      optional(choice(
        seq('.', field('symbol', $.identifier)),
        seq('.', '*'),
        seq(':', field('symbol', $.identifier), repeat(seq(',', field('symbol', $.identifier))))
      ))
    )),

    _statement: $ => choice(
      $.expression,
      $.function_decl,
      $.class_decl,
      $.do_statement,
      $.if_statement,
      $.try_statement,
      $.defer_statement,
      $.with_statement,
      $.switch_statement,
      $.loop_statement,
      $.repeat_statement,
      $.while_statement,
      $.for_statement,
      $.continue_statement,
      $.break_statement,
      $.fallthrough_statement,
      $.return_statement,
      $.throw_statement,
      $.assert_statement
    ),

    // Statements

    public_statement: $ => seq(
      'public',
      choice(
        $.function_decl,
        $.class_decl,
        $.variable_definition
      )
    ),

    compound_statement: $ => seq(
      '{',
      repeat(choice($._statement, ';')),
      '}'
    ),

    do_statement: $ => seq('do', $.compound_statement),

    if_statement: $ => seq(
      'if',
      $._rhs_expression,
      $.compound_statement,
      repeat(seq(
        'else',
        'if',
        $._rhs_expression,
        $.compound_statement
      )),
      optional(seq(
        'else',
        $.compound_statement
      ))
    ),

    try_statement: $ => seq(
      'try',
      $.compound_statement,
      $.catch_clause
    ),

    catch_clause: $ => seq(
      'catch',
      choice(
        $._catch_exception,
        seq('(', $._catch_exception, ')')
      ),
      $.compound_statement
    ),

    _catch_exception: $ => seq(
      choice('var', 'const'),
      $.variable_decl
    ),

    defer_statement: $ => seq('defer', $.compound_statement),

    with_statement: $ => seq(
      'with',
      choice(
        $._with_expression,
        seq('(', $._with_expression, ')')
      ),
      $.compound_statement
    ),

    _with_expression: $ => seq(
      $.with_object_expression,
      repeat(seq(',', $.with_object_expression))
    ),

    with_object_expression: $ => prec('with', seq(
      optional(seq(
        'const',
        $.variable_decl,
        '='
      )),
      $._rhs_expression
    )),

    switch_statement: $ => seq(
      'switch',
      $._rhs_expression,
      '{',
      repeat(choice(
        $.switch_case,
        $.default_case)),
      '}'
    ),

    switch_case: $ => seq(
      'case',
      $._rhs_expression,
      repeat(seq(',', $._rhs_expression)),
      optional(':'),
      '{',
      repeat1(choice($._statement, ';')),
      '}'
    ),

    default_case: $ => seq(
      'default',
      optional(':'),
      '{',
      repeat1(choice($._statement, ';')),
      '}'
    ),

    loop_statement: $ => seq('loop', $.compound_statement),

    repeat_statement: $ => prec.left(seq(
      'repeat',
      $.compound_statement,
      'while',
      $._rhs_expression
    )),

    while_statement: $ => seq('while', $._rhs_expression, $.compound_statement),

    for_statement: $ => seq('for', $._for_loop_control, $.compound_statement),

    _for_loop_control: $ => choice(
      $._for_in_expression,
      seq('(', $._for_in_expression, ')')
    ),

    _for_in_expression: $ => seq(
      choice(
        $.var_list,
        $.const_list,
        $._identifier_list
      ),
      'in',
      $._rhs_expression
    ),

    continue_statement: _ => 'continue',

    break_statement: _ => 'break',

    fallthrough_statement: _ => 'fallthrough',

    return_statement: $ => prec.right(seq(
      'return',
      optional($._rhs_expression)
    )),

    throw_statement: $ => prec.left(seq('throw', $._rhs_expression)),

    assert_statement: $ => prec.left(seq('assert', $._rhs_expression)),

    // Function statement

    function_decl: $ => seq(
      'fun',
      field('name', $.identifier),
      field('parameters', optional($.parameter_list)),
      $.compound_statement
    ),

    // Function arguments

    parameter_list: $ => prec.left('parameters', seq(
      '(',
      optional(seq(
        $._parameter_definition,
        repeat(seq(',', $._parameter_definition))
      )),
      ')'
    )),

    _parameter_definition: $ => choice(
      '_',
      $.parameter,
      $.default_parameter,
      $.list_parameter
    ),

    list_parameter: $ => seq($.parameter, '...'),

    default_parameter: $ => seq($.parameter, '=', $._rhs_expression),

    parameter: $ => prec('parameters', field('parameter', $.identifier)),

    // Class statement

    class_decl: $ => seq(
      'class',
      field('name', $.identifier),
      optional($.extends_decl),
      $.class_body
    ),

    extends_decl: $ => seq('extends', $._member_expression),

    class_body: $ => seq(
      '{',
      repeat($.class_member),
      '}'
    ),

    class_member: $ => choice(
      $.constructor_literal,
      $.function_decl,
      $.data_member
    ),

    data_member: $ => seq(
      'var',
      field('name', $.identifier),
      '=',
      $._rhs_expression
    ),

    constructor_literal: $ => seq(
      'constructor',
      optional(field('parameters', $.parameter_list)),
      $.compound_statement
    ),

    // Expressions

    expression: $ => choice(
      $.assignment,
      $.arithmetic_assignment,
      $.variable_definition,
      $._rhs_expression
    ),

    assignment: $ => seq(
      $._assignment_target_list,
      '=',
      $._rhs_expression
    ),

    arithmetic_assignment: $ => seq(
      $._mutable_assignment_target,
      $.arithmetic_assignment_operator,
      $._rhs_expression
    ),

    variable_definition: $ => seq(
      choice(
        $.var_list,
        $.const_list
      ),
      '=',
      $._rhs_expression
    ),

    var_list: $ => seq('var', $._identifier_decl_list),

    const_list: $ => seq('const', $._identifier_decl_list),

    _identifier_decl_list: $ => choice($.variable_decl, $._multiple_identifiers_decl),

    variable_decl: $ => field('variable', $.identifier),

    _multiple_identifiers_decl: $ => seq(
      $._identifier_decl_or_placeholder,
      ',',
      $._identifier_decl_or_placeholder,
      repeat(seq(',', $._identifier_decl_or_placeholder))
    ),

    _identifier_decl_or_placeholder: $ => choice(
      $.variable_decl,
      '_'
    ),

    _identifier_list: $ => choice($.identifier, $._multiple_identifiers),

    _multiple_identifiers: $ => seq(
      $._identifier_or_placeholder,
      ',',
      $._identifier_or_placeholder,
      repeat(seq(',', $._identifier_or_placeholder))
    ),

    _identifier_or_placeholder: $ => choice(
      $.identifier,
      '_'
    ),

    _assignment_target_list: $ => choice(
      $._mutable_assignment_target,
      $._multi_assignment_target_list
    ),

    _multi_assignment_target_list: $ => seq(
      $._assignment_target,
      ',',
      $._assignment_target,
      repeat(seq(',', $._assignment_target))
    ),

    _mutable_assignment_target: $ => choice(
      field('name', $.identifier),
      $.refinement
    ),

    _assignment_target: $ => choice(
      $._mutable_assignment_target,
      '_'
    ),

    _rhs_expression: $ => choice(
      $._stream_expression,
      $.yield_expression
    ),

    yield_expression: $ => prec.right('yield', seq(
      'yield',
      $._stream_expression
    )),

    _stream_expression: $ => prec.left('stream', seq(
      repeat(seq(
        $._conditional_expression,
        '->'
      )),
      $._conditional_expression
    )),

    _conditional_expression: $ => prec.left('conditional', choice(
      $._binary_expression,
      $.conditional_expression
    )),

    conditional_expression: $ => prec.left('conditional', seq(
      $._binary_expression,
      '?',
      $._conditional_expression,
      ':',
      $._conditional_expression
    )),

    _binary_expression: $ => choice(
      $.binary_expression,
      $._unary_expression
    ),

    binary_expression: $ => choice(
      prec.left( 'logical',        seq($._binary_expression, $.logical_operator,        $._binary_expression)),
      prec.left( 'comparison',     seq($._binary_expression, $.comparison_operator,     $._binary_expression)),
      prec.left( 'bitwise',        seq($._binary_expression, $.bitwise_operator,        $._binary_expression)),
      prec.left( 'addition',       seq($._binary_expression, $.additive_operator,       $._binary_expression)),
      prec.left( 'multiplication', seq($._binary_expression, $.multiplicative_operator, $._binary_expression))
    ),

    _unary_expression: $ => prec.right('unary', choice(
      $.unary_expression,
      $._member_expression
    )),

    unary_expression: $ => seq(
      $.unary_operator,
      $._unary_expression
    ),

    // Operators

    arithmetic_assignment_operator: _ => choice(
      '+=',
      '-=',
      '++=',
      '*=',
      '/=',
      '%=',
      '&=',
      '|=',
      '^=',
      '<<=',
      '>>=',
      '>>>='
    ),

    comparison_operator: _ => choice(
      '==',
      '!=',
      '<=',
      '>=',
      '<',
      '>',
      'in',
      'instanceof',
      'propertyof'
    ),

    bitwise_operator: _ => choice(
      '<<',
      '>>',
      '>>>',
      '&',
      '|',
      '^'
    ),

    additive_operator: _ => choice(
      '+',
      '-',
      '++'
    ),

    multiplicative_operator: _ => choice(
      '*',
      '/',
      '%'
    ),

    logical_operator: _ => choice(
      '&&',
      '||'
    ),

    unary_operator: _ => choice(
      'typeof',
      'delete',
      '+',
      '-',
      '~',
      '!'
    ),

    // Member specification

    _member_expression: $ => prec('member', choice(
      $._primary_expression,
      $.function_literal,
      $.class_literal,
      $.invocation,
      $.refinement
    )),

    function_literal: $ => choice(
      $._simple_function_literal,
      $._compound_function_literal
    ),

    _simple_function_literal: $ => seq(
      choice(
        prec('parameters', '_'),
        $.parameter,
        field('parameters', $.parameter_list)
      ),
      '=>',
      $._rhs_expression
    ),

    _compound_function_literal: $ => seq(
      'fun',
      optional(field('parameters', $.parameter_list)),
      $.compound_statement
    ),

    class_literal: $ => seq(
      'class',
      optional($.extends_decl),
      $.class_body
    ),

    invocation: $ => prec.left('invocation', seq(
      $._member_expression,
      '(',
      field('arguments', optional($.argument_list)),
      ')'
    )),

    argument_list: $ => choice(
      $._named_argument_list,
      $._unnamed_argument_list
    ),

    _named_argument_list: $ => seq(
      $._named_argument,
      repeat(seq(',', $._named_argument))
    ),

    _named_argument: $ => seq(
      field('argument', $.identifier),
      '=',
      $._rhs_expression
    ),

    _unnamed_argument_list: $ => seq(
      $._unnamed_argument,
      repeat(seq(',', $._unnamed_argument))
    ),

    _unnamed_argument: $ => seq(
      $._rhs_expression,
      optional('...')
    ),

    refinement: $ => prec.left('refinement', seq(
      $._member_expression,
      choice(
        $._array_index_refinement,
        $._array_range_refinement,
        $._identifier_refinement,
        $._literal_refinement
      )
    )),

    _array_index_refinement: $ => seq(
      '[',
      optional('?'),
      $._rhs_expression,
      ']'
    ),

    _array_range_refinement: $ => seq(
      '[',
      optional($._rhs_expression),
      ':',
      optional($._rhs_expression),
      ']'
    ),

    _identifier_refinement: $ => seq(
      '.',
      optional('?'),
      field('property', alias($.identifier, $.property_identifier))
    ),

    _literal_refinement: $ => seq(
      '.',
      optional('?'),
      $._string
    ),

    _primary_expression: $ => prec('primary', choice(
      $.this,
      $.super,
      $.line,
      field('name', $.identifier),
      $.number,
      $.float_number,
      $._string,
      $.array,
      $.object,
      $.true,
      $.false,
      $.void,
      seq('(', $._rhs_expression, ')')
    )),

    this: _ => 'this',

    super: _ => 'super',

    line: _ => '__line__',

    true: _ => 'true',

    false: _ => 'false',

    void: _ => 'void',

    array: $ => seq(
      '[',
      optional(seq(
        $.array_element,
        repeat(seq(',', $.array_element)),
        optional(',')
      )),
      ']'
    ),

    array_element: $ => seq(
      $._rhs_expression,
      optional('...')
    ),

    object: $ => seq(
      '{',
      optional(seq(
        $.property,
        repeat(seq(',', $.property))
      )),
      '}'
    ),

    property: $ => seq(
      choice($._string, field('property', alias($.identifier, $.property_identifier))),
      ':',
      $._rhs_expression
    ),

    number: _ => token(choice(
      /0[bB][01_]+/,
      /0[xX][0-9a-fA-F_]+/,
      /0|[1-9][0-9_]*/
    )),

    float_number: _ => token(choice(
      /(0|[1-9][0-9_]*)[.][0-9_]*([eEpP][+-]?(0|[1-9][0-9_]*))?/,
      /(0|[1-9][0-9_]*)[eEpP][+-]?(0|[1-9][0-9_]*)/
    )),

    _string: $ => choice(
      $.string_literal,
      $.formatted_string
    ),

    formatted_string: $ => seq(
      $.string_literal_begin,
      $._rhs_expression,
      repeat(seq(
        ')',
        $.string_literal_continuation,
        $._rhs_expression
      )),
      ')',
      $.string_literal_end
    ),

    comment: _ => token(choice(
      seq('#', /[^\r\n\u2028\u2029]*/),
      seq('//', /[^\r\n\u2028\u2029]*/),
      seq('/*', /[^*]*\*+([^/*][^*]*\*+)*/, '/')
    )),

    _whitespace: _ => /[ \u000B\u000C\u00A0\uFEFF]/,

    _eol: _ => /[\r\n\u2028\u2029]/,

    identifier: _ => /[a-zA-Z_][a-zA-Z0-9_]*/,

    string_literal_begin: _ => seq(/"([^"\\\r\n\u2028\u2029]|\\([fnrtv\\"0]|x[0-9a-fA-F][0-9a-fA-F]|x\{[0-9a-fA-F]+\}))*/, '\\('),

    string_literal_continuation: _ => seq(/([^"\\\r\n\u2028\u2029]|\\([fnrtv\\"0]|x[0-9a-fA-F][0-9a-fA-F]|x\{[0-9a-fA-F]+\}))*/, '\\('),

    string_literal_end: _ => /([^"\\\r\n\u2028\u2029]|\\([fnrtv\\"0]|x[0-9a-fA-F][0-9a-fA-F]|x\{[0-9a-fA-F]+\}))*"/,

    string_literal: _ => /[rR]"[^"]*"|"([^"\\\r\n\u2028\u2029]|\\([fnrtv\\"0]|x[0-9a-fA-F][0-9a-fA-F]|x\{[0-9a-fA-F]+\}))*"/
  }
});
