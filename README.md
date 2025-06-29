# weighted-string-parser-node

**Parse Weighted String** parses a string with optional parentheses (escaped or unescaped with weights) and returns
a string with weights removed, a list of weighted terms, and a list of the weights.

Nesting of terms is not currently supported.

Input:

`a (bog bear)++ in a green chundle factory, with (blue)- (greezles)-- \(credit: Bog Magazine\)`

Outputs:

`a bog bear in a green chundle factory, with blue greezles (credit: Bog Magazine)`
`['bog bear', 'blue', 'greezles']`
`[1.21, 0.9, 0.81]`
