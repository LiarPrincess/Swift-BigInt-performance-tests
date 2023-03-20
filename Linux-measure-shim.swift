#if os(Linux)
#if swift(<5.7)
#if (arch(i386) || arch(x86_64)) && !os(Windows) && !os(Android)
private typealias Duration = Float80
#else
private typealias Duration = Double
#endif

extension Duration {
  fileprivate static func seconds(_ n: Int) -> Duration {
    return Duration(exactly: n)!
  }

  fileprivate static func / (lhs: Duration, rhs: Int) -> Duration {
    let r = Duration(exactly: rhs)!
    return lhs / r
  }
}

private struct ContinuousClock {
  fileprivate func measure(_ fn: () -> Void) -> Duration {
    let start = DispatchTime.now()
    fn()
    let end = DispatchTime.now()
    let nano = end.uptimeNanoseconds - start.uptimeNanoseconds
    let nanoDuration = Duration(exactly: nano)!
    return nanoDuration / 1_000_000_000.0
  }
}
#endif // #if swift(<5.7)

private class XCTMetric {}
private class XCTClockMetric: XCTMetric {}

private struct XCTMeasureOptions {
  fileprivate static let `default` = XCTMeasureOptions()
}

extension XCTestCase {
  fileprivate func measure(
    metrics: [XCTMetric],
    options: XCTMeasureOptions,
    fn: () -> Void
  ) {
    // Create static values, fill cache, etc.
    fn()

    let clock = ContinuousClock()
    var results = [Duration]()

    for _ in 0..<10 {
      let elapsed = clock.measure(fn)
      results.append(elapsed)
    }

    let withoutExtremes = results.sorted().dropFirst().dropLast()
    let totalDuration = withoutExtremes.reduce(Duration.seconds(0), +)
    let averageDuration = totalDuration / withoutExtremes.count
    print("average: \(averageDuration), values: \(results)")
  }
}
#endif // #if os(Linux)
