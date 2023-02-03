# string

|                         | 🐧 swift_numerics | 🐧 Violet                                                    | 🐧 attaswift                                                    |
| ----------------------- | ---------------- | ----------------------------------------------------------- | -------------------------------------------------------------- |
| test_string_fromRadix10 | 0.2386572415     | <span style="color:#39a275">0.011443098625 (20.9x)</span>   | <span style="color:#39a275">0.025662900375 (9.3x)</span>       |
| test_string_fromRadix16 | 0.202112097625   | <span style="color:#39a275">0.010199524125 (19.8x)</span>   | <span style="color:#39a275">0.016070078875 (12.6x)</span>      |
| test_string_toRadix10   | 0.46252024925    | <span style="color:#39a275">0.027593412875 (16.8x)</span>   | <span style="color:#39a275">0.03904019475 (11.8x)</span>       |
| test_string_toRadix16   | 1.61222800225    | <span style="color:#39a275">0.0136527455 (1.18e+02x)</span> | <span style="color:#39a275">0.009648846375 (1.67e+02x)</span>  |
| TOTAL                   | 2.515517590625   | <span style="color:#39a275">0.062888781125 (40.0x)</span>   | <span style="color:#39a275">0.09042202037500001 (27.8x)</span> |

Parsing from string:
- both `Violet` and `attaswift` are significantly faster (~20x)
- already discussed in initial post (see above)

To string:
- both `Violet` and `attaswift` are significantly faster (16x for decimal and 100x for 16)
- radix 16 takes more time than radix 10 in `swift_numerics`! Normally bigger radix -> faster calculation (because we divide by bigger number). This is weird.
- `Violet` has an [additional specialization](https://github.com/LiarPrincess/Violet/blob/fe662b422346b5b0a4ac2b86333adad59ff434a6/Sources/BigInt/BigIntHeap%2BDescription%2BToString.swift#L56) for powers of 2. The code is quite complicated, but without it `Violet` is 'only' 50x faster than `swift_numerics` (instead of 120x now). Though `attaswift` is the fastest getting >150x every time I run this test.

# unary

|                       | 🐧 swift_numerics | 🐧 Violet                                                  | 🐧 attaswift                                               |
| --------------------- | ---------------- | --------------------------------------------------------- | --------------------------------------------------------- |
| test_unary_plus_int   | 2.1575e-07       | 2.3175e-07 (0.931x)                                       | 2.22125e-07 (0.971x)                                      |
| test_unary_plus_big   | 2.1875e-07       | 2.26875e-07 (0.964x)                                      | <span style="color:#df1c44">4.30875e-07 (0.508x)</span>   |
| test_unary_minus_int  | 0.003008425      | <span style="color:#df1c44">0.0043980425 (0.684x)</span>  | <span style="color:#39a275">9.0998875e-04 (3.31x)</span>  |
| test_unary_minus_big  | 0.00765690125    | <span style="color:#39a275">0.00682969625 (1.12x)</span>  | <span style="color:#39a275">0.00137740875 (5.56x)</span>  |
| test_unary_invert_int | 0.00256642375    | <span style="color:#df1c44">0.00567599 (0.452x)</span>    | <span style="color:#df1c44">0.00464572875 (0.552x)</span> |
| test_unary_invert_big | 0.00648165625    | <span style="color:#df1c44">0.008457895 (0.766x)</span>   | <span style="color:#df1c44">0.00743845125 (0.871x)</span> |
| TOTAL                 | 0.00197178375    | <span style="color:#df1c44">0.00253667275 (0.777x)</span> | <span style="color:#39a275">0.001438013125 (1.37x)</span> |

Plus:
- all of the projects use the default implementation from protocol
- if we wrote it by hand then it would be ~1000 slower (tested on `Violet`)

Minus:
- `swift_numerics` and `Violet` have the same performance
- `attaswift` is 5.5x faster than `swift_numerics`/`Violet`
  - in `attaswift` unary '`-`' flips the sign and retains `magnitude` -> no `memcpy`

    ```Swift
    struct BigInt {
      enum Sign {
        case plus
        case minus
      }

      var sign: Sign
      var magnitude: BigUInt
    }
    ```

  - `Violet` stores both sign and magnitude on the heap -> unary '`-`' has to `memcpy` and change sign.
  - `swift_numerics` uses 2-complement -> `memcpy`.

- in `Violet` I wanted to store the sign in the pointer to get the same behavior as `attaswift`, but I already use the tagged pointer to differentiate between small inlined `Int32` and heap allocated storage. I didn't want to complicate it too much.

Invert:
- `swift_numerics` is the fastest
- `Violet` sucks, implemented as `~a = negate(a+1)`.

# add, sub

|                           | 🐧 swift_numerics | 🐧 Violet                                                       | 🐧 attaswift                                               |
| ------------------------- | ---------------- | -------------------------------------------------------------- | --------------------------------------------------------- |
| test_binary_add_int       | 0.051279978375   | <span style="color:#39a275">0.019060819 (2.69x)</span>         | <span style="color:#39a275">0.019951840375 (2.57x)</span> |
| test_binary_add_int_inout | 0.05192916475    | <span style="color:#39a275">0.02076205525 (2.5x)</span>        | <span style="color:#39a275">0.020384483625 (2.55x)</span> |
| test_binary_add_big       | 0.090885631375   | <span style="color:#39a275">0.068677264125 (1.32x)</span>      | 0.09213794875 (0.986x)                                    |
| test_binary_add_big_inout | 0.091238936125   | <span style="color:#39a275">0.07089660825 (1.29x)</span>       | 0.093134512375 (0.98x)                                    |
| test_binary_sub_int       | 0.05545868675    | <span style="color:#39a275">0.01689674575 (3.28x)</span>       | <span style="color:#39a275">0.020806254 (2.67x)</span>    |
| test_binary_sub_int_inout | 0.055421533875   | <span style="color:#39a275">0.0181362525 (3.06x)</span>        | <span style="color:#39a275">0.021699335375 (2.55x)</span> |
| test_binary_sub_big       | 0.10988923175    | <span style="color:#39a275">0.0616967295 (1.78x)</span>        | <span style="color:#39a275">0.094400776375 (1.16x)</span> |
| test_binary_sub_big_inout | 0.11059954725    | <span style="color:#39a275">0.064022515375 (1.73x)</span>      | <span style="color:#39a275">0.0948824495 (1.17x)</span>   |
| TOTAL                     | 0.61670271025    | <span style="color:#39a275">0.34014898974999996 (1.81x)</span> | <span style="color:#39a275">0.457397600375 (1.35x)</span> |

Add:
- `Violet` is ~1.3x faster than `swift_numerics`/`attaswift`, I have no idea why

Sub:
- `Violet` is ~1.7x faster than `swift_numerics`
- `Violet` is written by hand
- `swift_numerics` uses `a-b = a+(-b)` which adds an additional operation (negation)

# mul, div, mod

|                           | 🐧 swift_numerics | 🐧 Violet                                                       | 🐧 attaswift                                                |
| ------------------------- | ---------------- | -------------------------------------------------------------- | ---------------------------------------------------------- |
| test_binary_mul_int       | 0.01139182425    | <span style="color:#df1c44">0.014233305375 (0.8x)</span>       | 0.01198791775 (0.95x)                                      |
| test_binary_mul_int_inout | 0.011383868125   | <span style="color:#df1c44">0.01474806 (0.772x)</span>         | 0.0118222155 (0.963x)                                      |
| test_binary_mul_big       | 0.306249964625   | <span style="color:#df1c44">0.6437740713750001 (0.476x)</span> | <span style="color:#df1c44">1.265580211625 (0.242x)</span> |
| test_binary_mul_big_inout | 0.3026384555     | <span style="color:#df1c44">0.6773388391249999 (0.447x)</span> | <span style="color:#df1c44">1.317255822875 (0.23x)</span>  |
| test_binary_div_int       | 0.04702716525    | <span style="color:#39a275">0.040465835 (1.16x)</span>         | 0.045738173375 (1.03x)                                     |
| test_binary_div_int_inout | 0.047955614      | <span style="color:#39a275">0.043014225125 (1.11x)</span>      | 0.04783864875 (1.0x)                                       |
| test_binary_div_big       | 0.31499209525    | <span style="color:#df1c44">0.6193281083750001 (0.509x)</span> | <span style="color:#df1c44">0.466792756125 (0.675x)</span> |
| test_binary_div_big_inout | 0.317832630125   | <span style="color:#df1c44">0.6465085275 (0.492x)</span>       | <span style="color:#df1c44">0.467630718875 (0.68x)</span>  |
| test_binary_mod_int       | 0.047138412625   | <span style="color:#39a275">0.040629697875 (1.16x)</span>      | 0.0463784975 (1.02x)                                       |
| test_binary_mod_int_inout | 0.04768970325    | <span style="color:#39a275">0.041022141125 (1.16x)</span>      | 0.04722941475 (1.01x)                                      |
| test_binary_mod_big       | 0.3145220225     | <span style="color:#df1c44">0.62251520575 (0.505x)</span>      | <span style="color:#df1c44">0.460031641625 (0.684x)</span> |
| test_binary_mod_big_inout | 0.314247153875   | <span style="color:#df1c44">0.625336668375 (0.503x)</span>     | <span style="color:#df1c44">0.457763088375 (0.686x)</span> |
| TOTAL                     | 2.083068909375   | <span style="color:#df1c44">4.028914685 (0.517x)</span>        | <span style="color:#df1c44">4.646049107125 (0.448x)</span> |

- `swift_numerics` is 2x faster than `Violet`/`attaswift`, I would have to check your implementation to see why.
- `Violet` and `attaswift` have the same problems in the same operations (just look at the colors). This is weird.

# and, or, xor

|                           | 🐧 swift_numerics   | 🐧 Violet                                                  | 🐧 attaswift                                                    |
| ------------------------- | ------------------ | --------------------------------------------------------- | -------------------------------------------------------------- |
| test_binary_and_int       | 0.04795710325      | <span style="color:#39a275">0.01881220425 (2.55x)</span>  | <span style="color:#df1c44">0.107330404 (0.447x)</span>        |
| test_binary_and_int_inout | 0.047626051125     | <span style="color:#39a275">0.019930581875 (2.39x)</span> | <span style="color:#df1c44">0.084286617125 (0.565x)</span>     |
| test_binary_and_big       | 0.068227646875     | <span style="color:#39a275">0.059329904875 (1.15x)</span> | <span style="color:#df1c44">0.208089841875 (0.328x)</span>     |
| test_binary_and_big_inout | 0.067888722625     | <span style="color:#39a275">0.061380784 (1.11x)</span>    | <span style="color:#df1c44">0.202151294 (0.336x)</span>        |
| test_binary_or_int        | 0.04778776375      | <span style="color:#39a275">0.020975489625 (2.28x)</span> | <span style="color:#df1c44">0.096837845875 (0.493x)</span>     |
| test_binary_or_int_inout  | 0.04753421575      | <span style="color:#39a275">0.021974519375 (2.16x)</span> | <span style="color:#df1c44">0.089842750375 (0.529x)</span>     |
| test_binary_or_big        | 0.067830007        | 0.062224270875 (1.09x)                                    | <span style="color:#df1c44">0.221035849 (0.307x)</span>        |
| test_binary_or_big_inout  | 0.067732202625     | 0.064179316 (1.06x)                                       | <span style="color:#df1c44">0.2315409725 (0.293x)</span>       |
| test_binary_xor_int       | 0.049874415625     | <span style="color:#39a275">0.02811704225 (1.77x)</span>  | <span style="color:#df1c44">0.07684390925 (0.649x)</span>      |
| test_binary_xor_int_inout | 0.047673133125     | <span style="color:#39a275">0.030724417625 (1.55x)</span> | <span style="color:#df1c44">0.076789383375 (0.621x)</span>     |
| test_binary_xor_big       | 0.068102042125     | 0.070041217875 (0.972x)                                   | <span style="color:#df1c44">0.228035474375 (0.299x)</span>     |
| test_binary_xor_big_inout | 0.069273103125     | 0.0730879375 (0.948x)                                     | <span style="color:#df1c44">0.217389360625 (0.319x)</span>     |
| TOTAL                     | 0.6975064070000001 | <span style="color:#39a275">0.530777686125 (1.31x)</span> | <span style="color:#df1c44">1.8401737023749998 (0.379x)</span> |

- `swift_numerics` and `Violet` are basically the same; maybe Violet is a tiny bit faster
- `attaswift` 3x slower

# shift

|                           | 🐧 swift_numerics | 🐧 Violet                                                  | 🐧 attaswift                                                    |
| ------------------------- | ---------------- | --------------------------------------------------------- | -------------------------------------------------------------- |
| test_shiftLeft_int        | 0.07946351575    | <span style="color:#39a275">0.02477458275 (3.21x)</span>  | <span style="color:#39a275">0.012218613875 (6.5x)</span>       |
| test_shiftLeft_int_inout  | 0.06727435225    | <span style="color:#39a275">0.024736001 (2.72x)</span>    | <span style="color:#39a275">0.015686431375 (4.29x)</span>      |
| test_shiftLeft_big        | 0.380767720375   | <span style="color:#39a275">0.051836405375 (7.35x)</span> | <span style="color:#39a275">0.188792119375 (2.02x)</span>      |
| test_shiftLeft_big_inout  | 0.400460559375   | <span style="color:#39a275">0.05112491025 (7.83x)</span>  | <span style="color:#39a275">0.03727303725 (10.7x)</span>       |
| test_shiftRight_int       | 0.033158581125   | <span style="color:#39a275">0.0224629195 (1.48x)</span>   | <span style="color:#39a275">0.0122984715 (2.7x)</span>         |
| test_shiftRight_int_inout | 0.05349652125    | <span style="color:#39a275">0.022619413875 (2.37x)</span> | <span style="color:#39a275">0.01296880825 (4.13x)</span>       |
| test_shiftRight_big       | 0.4792015745     | <span style="color:#39a275">0.04791361225 (10.0x)</span>  | <span style="color:#39a275">0.041860571875 (11.4x)</span>      |
| test_shiftRight_big_inout | 0.47981406025    | <span style="color:#39a275">0.05261043 (9.12x)</span>     | <span style="color:#39a275">0.034685680375 (13.8x)</span>      |
| TOTAL                     | 1.973636884875   | <span style="color:#39a275">0.298078275 (6.62x)</span>    | <span style="color:#39a275">0.35578373387500006 (5.55x)</span> |


Left:
- `Violet`/`attaswift` are 7x faster than `swift_numerics`
- there is something really weird in `attaswift -> test_shiftLeft_big`, the `inout` is on pair with `Violet`, but the normal version is much slower. Ultra repeatable, occurs every time.

Right:
- `Violet`/`attaswift` are >9x faster than `swift_numerics` (`attaswift` gets >10x every time I run this test)

# Conclusions

| Operation        | Possible improvement                | Note                                                                                                  |
| ---------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `String` parsing | 20x                                 | Discussed in initial post                                                                             |
| `toString`       | 15x (100x if radix is a power of 2) | Radix 16 is slower than radix 10?                                                                     |
| Unary `+`        | -                                   | Do not write by hand, it is 1000x slower                                                              |
| Unary `-`        | 5.5x (see note)                     | Storing `sign` inline and `magnitude` on the heap is much faster (obviously, but now we have numbers) |
| Unary `~`        | -                                   |                                                                                                       |
| Binary `+`       | 1.3x                                | No idea why `Violet` is faster every time                                                             |
| Binary `-`       | 1.7x                                | Implemented as `a-b = a+(-b)`, writing it by hand may be faster (`Violet` does this)                  |
| Binary `*/%`     | -                                   | `swift_numerics` is 2x faster than `Violet`/`attaswift`???                                            |
| Binary `&\|^`    | -                                   |                                                                                                       |
| Shifts           | 9x (maybe 12x)                      |                                                                                                       |
