class Cloaken < Formula
  include Language::Python::Shebang

  desc "Hide macOS apps from Dock/Cmd+Tab by toggling LSUIElement"
  homepage "https://github.com/woxidi/cloaken"
  url "https://github.com/woxidi/cloaken/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "b3331345b4d0d0094557ead2a37cf8912d4c210f0a38869508ad39191d659c8c"
  license "MIT"
  version "0.1.0"

  depends_on "python@3.12"

  def install
    bin.install "cloaken.py" => "cloaken"
    rewrite_shebang detected_python_shebang(use_python_from_path("python3")), bin/"cloaken"
  end

  test do
    help_output = shell_output("#{bin}/cloaken --help")
    assert_match "LSUIElement", help_output
    assert_match "APP_PATH", help_output
  end
end
