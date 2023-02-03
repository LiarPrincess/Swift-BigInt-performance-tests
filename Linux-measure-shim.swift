#if os(Linux)
private class XCTMetric {}
private class XCTClockMetric: XCTMetric {}

private struct XCTMeasureOptions {
  fileprivate static let `default` = XCTMeasureOptions()
}

extension XCTestCase {
  fileprivate func measure(metrics: [XCTMetric], options: XCTMeasureOptions, fn: () -> ()) {
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
