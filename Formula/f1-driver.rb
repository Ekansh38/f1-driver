class F1Driver < Formula
  desc "Top-down F1 racing simulator with signed lap times"
  homepage "https://github.com/Ekansh38/f1-driver"
  version "1.0.1"

  on_macos do
    on_arm do
      url "https://github.com/Ekansh38/f1-driver/releases/download/v1.0.1/f1-driver-macos-arm64.tar.gz"
      sha256 "900e07788394f8fcb757690777d63a026c538f2f6890cfecc3a901ce53ca95e6"
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
