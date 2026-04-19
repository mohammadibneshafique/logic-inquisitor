"""
demo/examples.py
Pre-loaded demo code samples for judges and first-time users.
Each covers a different language and bug type from the taxonomy.
"""

from typing import TypedDict


class DemoExample(TypedDict):
    id: str
    label: str
    language: str
    description: str
    code: str


DEMO_EXAMPLES: list[DemoExample] = [
    {
        "id": "c_off_by_one",
        "label": "🔵 C — Array Boundary Bug",
        "language": "c",
        "description": "Classic off-by-one error in a C array loop",
        "code": """\
#include <stdio.h>

int main() {
    int arr[5] = {10, 20, 30, 40, 50};
    int sum = 0;

    for (int i = 0; i <= 5; i++) {
        sum += arr[i];
    }

    printf("Sum: %d\\n", sum);
    return 0;
}""",
    },
    {
        "id": "java_null_deref",
        "label": "🔴 Java — NullPointerException",
        "language": "java",
        "description": "Unchecked null dereference from a cache lookup",
        "code": """\
import java.util.HashMap;
import java.util.Map;

public class UserService {
    private Map<String, String> cache = new HashMap<>();

    public String getUserEmail(String userId) {
        String email = cache.get(userId);
        return email.toLowerCase();
    }

    public void processUsers(String[] userIds) {
        for (String id : userIds) {
            String email = getUserEmail(id);
            System.out.println("Processing: " + email);
        }
    }

    public static void main(String[] args) {
        UserService service = new UserService();
        service.processUsers(new String[]{"user1", "user2", "user3"});
    }
}""",
    },
    {
        "id": "python_recursion",
        "label": "🟡 Python — Recursion Bug",
        "language": "python",
        "description": "Fibonacci with a subtle missing base case",
        "code": """\
def fibonacci(n):
    if n == 0:
        return 0
    return fibonacci(n - 1) + fibonacci(n - 2)


def main():
    for i in range(10):
        print(f"fib({i}) = {fibonacci(i)}")


main()""",
    },
    {
        "id": "logic_kadane",
        "label": "🟣 Logic — Algorithm Edge Case",
        "language": "logic_problem",
        "description": "Kadane's algorithm fails on all-negative arrays",
        "code": """\
Problem: Find the maximum subarray sum in an array of integers.

My approach:
1. Initialize max_sum = 0
2. Initialize current_sum = 0
3. For each element in the array:
   - Add element to current_sum
   - If current_sum > max_sum, update max_sum
   - If current_sum < 0, reset current_sum to 0
4. Return max_sum

Test case 1: [-2, 1, -3, 4, -1, 2, 1, -5, 4]
My output: 6
Expected:  6  ✓  (correct)

Test case 2: [-5, -3, -1, -2]
My output: 0
Expected: -1  ✗  (wrong!)

Why does my algorithm fail when ALL numbers in the array are negative?
What assumption did I make that does not hold for this input?""",
    },
]

DEMO_LABELS = ["— Select a demo example —"] + [ex["label"] for ex in DEMO_EXAMPLES]


def get_demo_by_label(label: str) -> DemoExample | None:
    """Look up a demo example by its display label."""
    for ex in DEMO_EXAMPLES:
        if ex["label"] == label:
            return ex
    return None
