extension BigInt {
  public var wordCount: Int {
    return self.storage.count
  }
}

// -----------------------------------------------------------------------------

private func _print(_ op: String, _ n: UInt) {
  print("\(op)|\(n)")
}

private func _print(_ op: String, _ lhs: BigInt, _ rhs: BigInt) {
  print("\(op)|\(lhs.wordCount)|\(rhs.wordCount)")
}

// Adapted from:
// https://github.com/apple/swift-numerics/pull/120 by Xiaodi Wu (xwu)
func π(count: Int) {
  var acc: BigInt = 0
  var num: BigInt = 1
  var den: BigInt = 1

  func extractDigit(_ n: UInt) -> UInt {
    _print("init", n)
    _print("mul", num, BigInt(n))
    var tmp = num * BigInt(n)
    _print("add", tmp, acc)
    tmp += acc
    _print("div", tmp, den)
    tmp /= den
    return tmp.words[0]
  }

  func eliminateDigit(_ d: UInt) {
    _print("init", d)
    _print("mul", den, BigInt(d))
    _print("sub", acc, den * BigInt(d))
    acc -= den * BigInt(d)
    _print("mul", acc, 10)
    acc *= 10
    _print("mul", num, 10)
    num *= 10
  }

  func nextTerm(_ k: UInt) {
    _print("init", k * 2 + 1)
    let k2 = BigInt(k * 2 + 1)
    _print("mul", num, 2)
    _print("add", acc, num * 2)
    acc += num * 2
    _print("mul", acc, k2)
    acc *= k2
    _print("mul", den, k2)
    den *= k2
    _print("init", k)
    _print("mul", num, BigInt(k))
    num *= BigInt(k)
  }

  var i = 0
  var k = 0 as UInt
  var string = ""

  while i < count {
    k += 1
    nextTerm(k)

    _print("greater_than", num, acc)
    if num > acc {
      continue
    }

    let d = extractDigit(3)
    if d != extractDigit(4) {
      continue
    }

    string.append("\(d)")
    i += 1

    if i.isMultiple(of: 10) {
      print("\(string)\t:\(i)")
      string = ""
    }

    eliminateDigit(d)
  }
}

π(count: 5000)
