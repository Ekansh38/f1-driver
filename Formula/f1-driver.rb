class F1Driver < Formula
  desc "Top-down F1 racing simulator with signed lap times"
  homepage "https://github.com/Ekansh38/f1-driver"
  version "1.0.0"

  on_macos do
    on_arm do
      url "https://github.com/Ekansh38/f1-driver/releases/download/v1.0.0/f1-driver-macos-arm64.tar.gz"
      sha256 "PLACEHOLDER_ARM64"
    end
    on_intel do
      url "https://github.com/Ekansh38/f1-driver/releases/download/v1.0.0/f1-driver-macos-x86_64.tar.gz"
      sha256 "PLACEHOLDER_X86"
    end
  end

  def install
    libexec.install Dir["f1-driver/*"]
    bin.write_exec_script libexec/"f1-driver"
  end

  test do
    assert_predicate bin/"f1-driver", :exist?
  end
end
