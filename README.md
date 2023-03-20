# Swift `BigInt` performance tests

This project runs performance tests for `BigInt` implementations from:
- `swift_numerics` - [this branch](https://github.com/LiarPrincess/swift-numerics/tree/13-Performance)
- `Violet` - [this branch](https://github.com/LiarPrincess/Violet/tree/swift-numerics) which is a `main` branch with all `swift_numerics` tests from all PRs
  - optimized for `Int32` range. In this tests only `0`, `-1` and `1` fall into this range, so it should not matter.
- `Violet XsProMax` - [this branch](https://github.com/LiarPrincess/Violet-BigInt-XsProMax). Violet implementation with following changes:
  - no small inlined integer - magnitude is always stored on the heap
  - no restrictions on the size - `isNegative` is stored in-line (and not on the heap like in Violet); `count` and `capacity` are on the heap because I don't want to stray too much from `Violet`.
- `attaswift` - [this branch](https://github.com/LiarPrincess/BigInt/tree/Performance-tests) which is a `main` branch with added performance tests

## Content

- `__main__.py` - main script to run tests; most of the time you will use this
- `multiple_run.py` - run tests multiple times in a loop; useful to combat random relative standard deviation spikes
- `multiple_group_by_test.py` - process results from `multiple_run.py`, so that they are grouped by test (instead of per run)

## How to read the results

Values in parens mean relative performance improvement vs the 1st implementation. For example:

|                         | 🐧 swift_numerics | 🐧 Violet                                                  | 🐧 attaswift                                              |
| ----------------------- | ---------------- | --------------------------------------------------------- | -------------------------------------------------------- |
| test_string_fromRadix10 | 0.2386572415     | <span style="color:#39a275">0.011443098625 (20.9x)</span> | <span style="color:#39a275">0.025662900375 (9.3x)</span> |

Means that `Violet` is 20.9 times faster than `swift_numerics` and `attaswift` is 9.3 times faster.

If you want you can also set `SHOW_RELATIVE_STANDARD_DEVIATION = True` inside the script.

## How to run

1. Clone all of the implementations mentioned above
2. Open `__main__.py` and modify:

    ```py
    # Path to: https://github.com/LiarPrincess/swift-numerics/tree/13-Performance
    # Branch: 13-Performance
    SWIFT_NUMERICS_PATH = '…'
    # Path to: https://github.com/LiarPrincess/Violet/tree/swift-numerics
    # Branch: swift-numerics
    VIOLET_PATH = '…'
    # Path to: https://github.com/LiarPrincess/BigInt/tree/Performance-tests
    # Branch: Performance-tests
    ATTASWIFT_PATH = '…'
    ```

3. Select which implementations to run:

    ```py
    # 1st entry is a reference implementation,
    # all of the others will be compared with it.
    IMPLEMENTATIONS = (
        SWIFT_NUMERICS,
        VIOLET,
        ATTASWIFT,
    )
    ```

4. Run `python3 .` in main dir (or F5 in VSCode)
