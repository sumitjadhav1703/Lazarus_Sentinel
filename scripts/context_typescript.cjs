// Read AST facts from bounded source text on stdin. No project config or source is executed.
'use strict';
const fs = require('node:fs');
const ts = require('../frontend/node_modules/typescript');

function parse(path, text) {
  const tree = ts.createSourceFile(path, text, ts.ScriptTarget.Latest, true);
  if (tree.parseDiagnostics.length) return null;
  const definitions = [], imports = [], calls = [], unknowns = [];
  const bindings = Object.create(null);
  const line = (offset) => tree.getLineAndCharacterOfPosition(offset).line + 1;
  const count = (name) => {
    if (name && ts.isIdentifier(name)) bindings[name.text] = (bindings[name.text] || 0) + 1;
  };
  function markWrite(node) {
    if (ts.isIdentifier(node)) count(node);
    else if (ts.isPropertyAccessExpression(node) || ts.isElementAccessExpression(node)) markWrite(node.expression);
    else if (ts.isParenthesizedExpression(node)) markWrite(node.expression);
    else if (ts.isArrayLiteralExpression(node)) {
      for (const entry of node.elements) markWrite(entry);
    } else if (ts.isObjectLiteralExpression(node)) {
      for (const entry of node.properties) markWrite(entry);
    } else if (ts.isShorthandPropertyAssignment(node)) markWrite(node.name);
    else if (ts.isPropertyAssignment(node)) markWrite(node.initializer);
    else if (ts.isSpreadElement(node) || ts.isSpreadAssignment(node)) markWrite(node.expression);
    else if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.EqualsToken) markWrite(node.left);
  }

  const hasModifier = (node, kind) => node.modifiers?.some((modifier) => modifier.kind === kind);

  function visit(node, owner, prefix) {
    const start = line(node.getStart(tree));
    const end = line(Math.max(node.getStart(tree), node.end - 1));
    if (ts.isBinaryExpression(node) && node.operatorToken.kind >= ts.SyntaxKind.FirstAssignment &&
        node.operatorToken.kind <= ts.SyntaxKind.LastAssignment) markWrite(node.left);
    if ((ts.isPrefixUnaryExpression(node) || ts.isPostfixUnaryExpression(node)) &&
        [ts.SyntaxKind.PlusPlusToken, ts.SyntaxKind.MinusMinusToken].includes(node.operator)) markWrite(node.operand);
    if ((ts.isForInStatement(node) || ts.isForOfStatement(node)) &&
        !ts.isVariableDeclarationList(node.initializer)) markWrite(node.initializer);
    if (ts.isDeleteExpression(node)) markWrite(node.expression);
    const isDefinition = ts.isFunctionDeclaration(node) || ts.isClassDeclaration(node) ||
      ts.isInterfaceDeclaration(node) || ts.isTypeAliasDeclaration(node) ||
      ts.isEnumDeclaration(node) || ts.isMethodDeclaration(node) ||
      (ts.isVariableDeclaration(node) && node.initializer &&
       (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer)));
    if (isDefinition && node.name && ts.isIdentifier(node.name)) {
      if (!ts.isVariableDeclaration(node) && !ts.isMethodDeclaration(node)) count(node.name);
      const name = prefix ? `${prefix}.${node.name.text}` : node.name.text;
      const index = definitions.length;
      definitions.push({
        name, start_line: start, end_line: end,
        owner,
        callable: ts.isFunctionDeclaration(node) && !!node.body && node.parent === tree,
        exported: !!hasModifier(node, ts.SyntaxKind.ExportKeyword),
      });
      owner = index;
      prefix = name;
    }
    if (ts.isVariableDeclaration(node) || ts.isParameter(node) || ts.isBindingElement(node) ||
        ts.isFunctionExpression(node) || ts.isClassExpression(node)) count(node.name);
    if (ts.isImportDeclaration(node) && ts.isStringLiteral(node.moduleSpecifier)) {
      const clause = node.importClause;
      const record = (name, alias, bind) => imports.push({
        module: node.moduleSpecifier.text, name, alias, bind, line: start, end_line: end, owner,
      });
      if (clause?.name) {
        count(clause.name);
        record('default', clause.name.text, !clause.isTypeOnly);
      }
      const named = clause?.namedBindings;
      if (named && ts.isNamespaceImport(named)) {
        count(named.name);
        record(null, named.name.text, !clause.isTypeOnly);
      } else if (named) {
        for (const item of named.elements) {
          count(item.name);
          record((item.propertyName || item.name).text, item.name.text, !clause.isTypeOnly && !item.isTypeOnly);
        }
      } else if (!clause?.name) {
        record(null, '', false);
      }
    } else if (ts.isExportDeclaration(node) && node.moduleSpecifier && ts.isStringLiteral(node.moduleSpecifier)) {
      imports.push({module: node.moduleSpecifier.text, name: null, alias: '', bind: false, line: start, end_line: end, owner});
    } else if (ts.isImportEqualsDeclaration(node)) {
      count(node.name);
      unknowns.push({start_line: start, kind: 'UNSUPPORTED_IMPORT'});
    }
    if (ts.isCallExpression(node)) {
      const fn = node.expression;
      if (fn.kind === ts.SyntaxKind.ImportKeyword || (ts.isIdentifier(fn) && fn.text === 'require')) {
        unknowns.push({start_line: start, kind: 'DYNAMIC_IMPORT'});
      } else if (ts.isIdentifier(fn) && fn.text === 'eval') {
        unknowns.push({start_line: start, kind: 'DYNAMIC_BINDING'});
      } else if (ts.isIdentifier(fn)) {
        calls.push({name: fn.text, line: start, end_line: end, owner});
      } else if (ts.isPropertyAccessExpression(fn) && ts.isIdentifier(fn.expression) && ts.isIdentifier(fn.name)) {
        calls.push({name: `${fn.expression.text}.${fn.name.text}`, line: start, end_line: end, owner});
      } else {
        unknowns.push({start_line: start, kind: 'UNRESOLVED_CALL'});
      }
    }
    if (definitions.length + imports.length + calls.length + unknowns.length > 30000) {
      throw new Error('CONTEXT_RECORD_LIMIT');
    }
    ts.forEachChild(node, (child) => visit(child, owner, prefix));
  }
  try {
    visit(tree, null, '');
    return { definitions, imports, calls, bindings, unknowns };
  } catch (error) {
    if (error instanceof RangeError) return null;
    throw error;
  }
}

const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const output = Object.create(null);
let bytes = 0;
for (const [path, text] of Object.entries(input)) {
  const record = parse(path, text);
  bytes += Buffer.byteLength(JSON.stringify(record));
  if (bytes > 16 * 1024 * 1024) throw new Error('CONTEXT_INDEX_SIZE_LIMIT');
  output[path] = record;
}
process.stdout.write(JSON.stringify(output));
