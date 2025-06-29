# Copyright (c) 2025 Jonathan S. Pollack (https://github.com/JPPhoto)

import re

from invokeai.invocation_api import (
    BaseInvocation,
    BaseInvocationOutput,
    InputField,
    InvocationContext,
    OutputField,
    invocation,
    invocation_output,
)


@invocation_output("weighted_string_output")
class WeightedStringOutput(BaseInvocationOutput):
    cleaned_text: str = OutputField(description="The input string with weights and parentheses removed")
    phrases: list[str] = OutputField(description="List of weighted phrases or words")
    weights: list[float] = OutputField(description="Associated weights for each phrase")
    positions: list[int] = OutputField(description="Start positions of each phrase in the cleaned string")


@invocation(
    "parse_weighted_string", title="Parse Weighted String", tags=["prompt", "weights", "parser"], version="1.0.1"
)
class ParseWeightedStringInvocation(BaseInvocation):
    """Parses a string containing weighted terms (e.g. `(word)++` or `word-`) and returns the cleaned string, list of terms, their weights, and positions."""

    text: str = InputField(description="The input string containing weighted expressions")

    def invoke(self, context: InvocationContext) -> WeightedStringOutput:
        s = self.text

        # Match unescaped parenthesized terms or bare words followed by +, -, or numbers
        # Group 1+2: (term)+weight with trailing space, punctuation, or EOS
        # Group 3+4: word+weight with trailing space, punctuation, or EOS
        pattern = r"""
            (?<!\\)\(([^()]+?)\)([\+\-]+|[-+]?\d*\.?\d+)(?=[\s,.;:!?)]|$)
            |
            \b(\w+)\b([\+\-]+|[-+]?\d*\.?\d+)(?=[\s,.;:!?)]|$)
        """
        words = []
        weights = []
        positions = []

        cleaned = []
        cursor = 0
        last_end = 0

        for match in re.finditer(pattern, s, flags=re.VERBOSE):
            start, end = match.span()

            # Append unchanged text from last_end to match start
            unchanged = s[last_end:start]
            cleaned.append(unchanged)
            cursor += len(unchanged)

            if match.group(1):  # Parenthesized
                word = match.group(1).strip()
                modifier = match.group(2)
            else:  # Bare word
                word = match.group(3).strip()
                modifier = match.group(4)

            if modifier.startswith("+"):
                weight = 1.1 ** len(modifier)
            elif modifier.startswith("-"):
                weight = 0.9 ** len(modifier)
            else:
                weight = float(modifier)

            words.append(word)
            weights.append(round(weight, 15))
            positions.append(cursor)

            cleaned.append(word)
            cursor += len(word)
            last_end = end

        # Append the tail of the string
        cleaned.append(s[last_end:])
        final = "".join(cleaned)

        # Unescape any escaped parens
        final = re.sub(r"\\([\(\)])", r"\1", final)

        return WeightedStringOutput(cleaned_text=final, phrases=words, weights=weights, positions=positions)
