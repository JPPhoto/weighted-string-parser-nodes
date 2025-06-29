# Copyright (c) 2025 Jonathan S. Pollack (https://github.com/JPPhoto)

import re
from typing import List

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
    phrases: List[str] = OutputField(description="List of weighted phrases or words")
    weights: List[float] = OutputField(description="Associated weights for each phrase")


@invocation(
    "parse_weighted_string", title="Parse Weighted String", tags=["prompt", "weights", "parser"], version="1.0.0"
)
class ParseWeightedStringInvocation(BaseInvocation):
    """Parses a string containing weighted terms (e.g. `(word)++` or `word-`) and returns the cleaned string, list of terms, and their weights."""

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

        def replacement(m):
            if m.group(1):  # Parenthesized
                word = m.group(1).strip()
                modifier = m.group(2)
            else:  # Bare word
                word = m.group(3).strip()
                modifier = m.group(4)

            if modifier.startswith("+"):
                weight = 1.1 ** len(modifier)
            elif modifier.startswith("-"):
                weight = 0.9 ** len(modifier)
            else:
                weight = float(modifier)

            words.append(word)
            weights.append(round(weight, 15))
            return word

        cleaned = re.sub(pattern, replacement, s, flags=re.VERBOSE)

        # Unescape any escaped parens
        cleaned = re.sub(r"\\([\(\)])", r"\1", cleaned)

        return WeightedStringOutput(cleaned_text=cleaned, phrases=words, weights=weights)
