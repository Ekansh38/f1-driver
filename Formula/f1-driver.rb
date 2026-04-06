class F1Driver < Formula
  desc "Top-down F1 racing simulator with signed lap times"
  homepage "https://github.com/Ekansh38/f1-driver"
  version "1.0.0"

  on_macos do
    on_arm do
      url "https://github.com/Ekansh38/f1-driver/releases/download/v1.0.0/f1-driver-macos-arm64.tar.gz"
      sha256 "fe3a60e04bed046a8e2820dacbf90fd57789d72b0e15792df9a0e318fdb925bb"
    end
  end

  def install
    libexec.install Dir["*"]
    bin.write_exec_script libexec/"f1-driver"
  end

  test do
    assert_predicate bin/"f1-driver", :exist?
  end
end
