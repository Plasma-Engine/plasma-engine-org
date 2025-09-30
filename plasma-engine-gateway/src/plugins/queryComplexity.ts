import { ApolloServerPlugin, GraphQLRequestListener } from '@apollo/server';
import { GraphQLError } from 'graphql';
import {
  DocumentNode,
  FieldNode,
  FragmentDefinitionNode,
  FragmentSpreadNode,
  InlineFragmentNode,
  OperationDefinitionNode,
  SelectionNode,
  getOperationAST,
} from 'graphql';
import { logger } from '../utils/logger';

interface ComplexityResult {
  score: number;
  depth: number;
  fields: string[];
}

export function QueryComplexityPlugin(maxComplexity: number): ApolloServerPlugin {
  return {
    async requestDidStart() {
      return {
        async didResolveOperation(requestContext): Promise<void> {
          const { request, document } = requestContext;

          if (!document) {
            return;
          }

          try {
            const complexity = calculateQueryComplexity(document, request.variables || {});

            logger.debug('Query complexity:', {
              operationName: request.operationName,
              complexity,
            });

            if (complexity.score > maxComplexity) {
              logger.warn('Query complexity exceeded:', {
                operationName: request.operationName,
                complexity: complexity.score,
                maxComplexity,
                fields: complexity.fields,
              });

              throw new GraphQLError('Query too complex', {
                extensions: {
                  code: 'QUERY_TOO_COMPLEX',
                  complexity: complexity.score,
                  maxComplexity,
                  depth: complexity.depth,
                },
              });
            }

            // Add complexity to context for logging
            (requestContext as any).complexity = complexity;
          } catch (error) {
            if (error instanceof GraphQLError) {
              throw error;
            }
            logger.error('Error calculating query complexity:', error);
          }
        },

        async willSendResponse(requestContext): Promise<void> {
          const complexity = (requestContext as any).complexity;
          if (complexity) {
            // Add complexity to response headers
            requestContext.response.http?.headers?.set(
              'X-Query-Complexity',
              complexity.score.toString()
            );
            requestContext.response.http?.headers?.set(
              'X-Query-Depth',
              complexity.depth.toString()
            );
          }
        },
      } as GraphQLRequestListener<any>;
    },
  };
}

function calculateQueryComplexity(
  document: DocumentNode,
  variables: Record<string, any>
): ComplexityResult {
  const operation = getOperationAST(document);
  if (!operation) {
    return { score: 0, depth: 0, fields: [] };
  }

  const fragments = getFragments(document);
  const fields: string[] = [];

  const complexity = calculateSelectionSetComplexity(
    operation.selectionSet.selections,
    fragments,
    variables,
    1,
    fields,
    []
  );

  return {
    score: complexity.score,
    depth: complexity.depth,
    fields: Array.from(new Set(fields)),
  };
}

function calculateSelectionSetComplexity(
  selections: ReadonlyArray<SelectionNode>,
  fragments: Map<string, FragmentDefinitionNode>,
  variables: Record<string, any>,
  currentDepth: number,
  fields: string[],
  visitedFragments: string[]
): { score: number; depth: number } {
  let totalScore = 0;
  let maxDepth = currentDepth;

  for (const selection of selections) {
    if (selection.kind === 'Field') {
      const field = selection as FieldNode;
      const fieldName = field.name.value;

      // Skip introspection fields
      if (fieldName.startsWith('__')) {
        continue;
      }

      fields.push(fieldName);

      // Base complexity for the field
      let fieldComplexity = 1;

      // Add complexity for arguments
      if (field.arguments && field.arguments.length > 0) {
        fieldComplexity += field.arguments.length * 0.5;

        // Check for pagination arguments
        for (const arg of field.arguments) {
          const argName = arg.name.value;
          const argValue = resolveArgumentValue(arg.value, variables);

          if (argName === 'first' || argName === 'limit' || argName === 'pageSize') {
            const limit = parseInt(argValue, 10);
            if (!isNaN(limit)) {
              // Add complexity based on requested items
              fieldComplexity += Math.min(limit, 100) * 0.1;
            }
          }
        }
      }

      // Add complexity for nested selections
      if (field.selectionSet) {
        const nested = calculateSelectionSetComplexity(
          field.selectionSet.selections,
          fragments,
          variables,
          currentDepth + 1,
          fields,
          visitedFragments
        );

        // Multiply complexity for list fields
        const multiplier = isListField(fieldName) ? 10 : 1;
        fieldComplexity += nested.score * multiplier;
        maxDepth = Math.max(maxDepth, nested.depth);
      }

      // Special cases for expensive fields
      if (isExpensiveField(fieldName)) {
        fieldComplexity *= 5;
      }

      totalScore += fieldComplexity;
    } else if (selection.kind === 'FragmentSpread') {
      const spread = selection as FragmentSpreadNode;
      const fragmentName = spread.name.value;

      if (visitedFragments.includes(fragmentName)) {
        continue; // Avoid infinite recursion
      }

      const fragment = fragments.get(fragmentName);
      if (fragment) {
        const nested = calculateSelectionSetComplexity(
          fragment.selectionSet.selections,
          fragments,
          variables,
          currentDepth,
          fields,
          [...visitedFragments, fragmentName]
        );

        totalScore += nested.score;
        maxDepth = Math.max(maxDepth, nested.depth);
      }
    } else if (selection.kind === 'InlineFragment') {
      const inline = selection as InlineFragmentNode;
      const nested = calculateSelectionSetComplexity(
        inline.selectionSet.selections,
        fragments,
        variables,
        currentDepth,
        fields,
        visitedFragments
      );

      totalScore += nested.score;
      maxDepth = Math.max(maxDepth, nested.depth);
    }
  }

  // Add depth penalty
  totalScore += currentDepth * 2;

  return { score: Math.ceil(totalScore), depth: maxDepth };
}

function getFragments(document: DocumentNode): Map<string, FragmentDefinitionNode> {
  const fragments = new Map<string, FragmentDefinitionNode>();

  for (const definition of document.definitions) {
    if (definition.kind === 'FragmentDefinition') {
      fragments.set(definition.name.value, definition);
    }
  }

  return fragments;
}

function resolveArgumentValue(value: any, variables: Record<string, any>): any {
  if (value.kind === 'Variable') {
    return variables[value.name.value];
  }

  if (value.kind === 'IntValue' || value.kind === 'FloatValue') {
    return value.value;
  }

  if (value.kind === 'StringValue' || value.kind === 'BooleanValue' || value.kind === 'EnumValue') {
    return value.value;
  }

  if (value.kind === 'ListValue') {
    return value.values.map((v: any) => resolveArgumentValue(v, variables));
  }

  if (value.kind === 'ObjectValue') {
    const obj: Record<string, any> = {};
    for (const field of value.fields) {
      obj[field.name.value] = resolveArgumentValue(field.value, variables);
    }
    return obj;
  }

  return null;
}

function isListField(fieldName: string): boolean {
  // Common list field patterns
  const listPatterns = [
    /^(list|items|results|edges|nodes|data|records|entries)/i,
    /s$/i, // Plural fields
  ];

  return listPatterns.some(pattern => pattern.test(fieldName));
}

function isExpensiveField(fieldName: string): boolean {
  // Fields known to be expensive
  const expensiveFields = [
    'search',
    'analyze',
    'aggregate',
    'statistics',
    'report',
    'export',
    'generateReport',
    'fullTextSearch',
    'complexQuery',
  ];

  return expensiveFields.includes(fieldName);
}

// Directive-based complexity calculation (for schemas that use @complexity directive)
export function DirectiveBasedComplexityPlugin(): ApolloServerPlugin {
  return {
    async requestDidStart() {
      return {
        async didResolveOperation(requestContext): Promise<void> {
          // This would integrate with schemas that have @complexity directives
          // Implementation would parse the schema and use directive values
          logger.debug('Directive-based complexity calculation not implemented yet');
        },
      } as GraphQLRequestListener<any>;
    },
  };
}