class Cloaken < Formula
  include Language::Python::Shebang

  desc "Hide macOS apps from Dock/Cmd+Tab by toggling LSUIElement"
  homepage "https://github.com/YOUR_GITHUB_USERNAME/cloaken"
  url "https://github.com/YOUR_GITHUB_USERNAME/cloaken/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_TARBALL_SHA256"
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
